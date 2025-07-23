import re
import os
import time
import traceback
from urllib.parse import urljoin
import json

import logger
import config
from .scraper import cover_json_data
from .mode_search import print_data
from utils import httprequest, functions
from utils.event import register_event
from utils.number_parser import get_number
from .scrapinglib.custom.javdb import Javdb

from lxml import etree
import openpyxl

columns  = ["number","title","actor","userrating","uservotes","release","magnet_link","magnet_meta","magnet_tags",]
title    = ["番号",  "标题",  "演员", "评分",      "人数",      "发布日期","磁力",       "内容",        "标签"]
downloaded_numbers = []

exit_now = False
def SIGINT_callback():
    global exit_now
    exit_now = True
    logger.info(f"SIGINT_callback: exit_now={exit_now}")
    
#https://javdb459.com/users/want_watch_videos
def run(arr:list, with_cover:bool):
    register_event("SIGINT", callback=SIGINT_callback)
    url = arr[0]
    xlsxfile = arr[1] if len(arr) > 1 else "scrapingurl.xlsx"
    xlsxfile = os.path.abspath(xlsxfile)

    dirs = ["/mnt/f/1","/mnt/f/downloaded","/mnt/f/store"]
    
    for dir in dirs:
        filelist = os.listdir(dir)
        for file in filelist:
            if os.path.isfile(os.path.join(dir,file)):
                downloaded_numbers.append(get_number(file))

    workbook = None
    sheet = None
    if os.path.exists(xlsxfile):
        logger.info(f"file [{xlsxfile}] already exists... ")
        workbook = openpyxl.load_workbook(xlsxfile)
        sheet = workbook.active
        header_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
        rows_to_delete = []
        for col_idx, header in enumerate(header_row):
            if header == "番号":
                for row_idx,row in enumerate(sheet.iter_rows(min_row=2, values_only=True),start=1):
                    number = row[col_idx]
                    if number:
                        if number in downloaded_numbers:
                            rows_to_delete.append(row_idx)
                        else:
                            downloaded_numbers.append(number)
                break
        if len(rows_to_delete) > 0:
            logger.info(f"delete {len(rows_to_delete)} rows in xlsx file.")
            for row_idx in sorted(rows_to_delete, reverse=True):
                sheet.delete_rows(row_idx)
    else:
        logger.info(f"file [{xlsxfile}] not exists, create new file... ")
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Data"  
        sheet.append(title)
    
    img_dir = None
    if with_cover:
        img_dir = xlsxfile + "_cover"
        functions.create_folder(img_dir)
        logger.info(f"scraping data from [{url}] save to [{xlsxfile}] img download to [{img_dir}]")

    javdb(url, sheet, img_dir)
    workbook.save(xlsxfile)

#url中存在page参数时只拉取本页数据，不含page参数时则自动翻页拉取全部数据
def javdb(url:str, sheet:openpyxl.worksheet.worksheet.Worksheet, img_dir:str) : 
    session = httprequest.request_session(cookies=Javdb.get_cookies())
    try:
        getOtherPage = 'page=' not in url
        pageAt = 1
        while True:
            if exit_now:
                break    
            resp = session.get(url)
            tree = etree.fromstring(resp.text, etree.HTMLParser()) 
            sleep()
            datalen = 0
            if 'want_watch_videos' in url:
                datalen = want_watch_videos(resp.url, tree, img_dir, pageAt, sheet, session)
            else:
                datalen = other(resp.url, tree, img_dir, pageAt, sheet, session)
                
            if not getOtherPage or datalen < 20:
                break
            pageAt += 1
            url = url + ('&' if "?" in url else '?') + 'page=' + str(pageAt)
            
    except Exception as e:
        logger.error(f"url scraper error. {e}")
        logger.error(f"{traceback.format_exc()}")

def want_watch_videos(baseurl:str, tree:etree._Element, img_dir:str, pageAt:int, sheet:openpyxl.worksheet.worksheet.Worksheet, session):
    tag_a = tree.xpath('//*[contains(@class,"movie-list")]/div/div/a')
    datalen = len(tag_a)
    logger.info(f"get {datalen} urls in page {pageAt}")

    for a in tag_a:
        if exit_now:
            break   
        detail_url = a.get('href')

        tag_num = a.find('div[@class="video-title"]/strong')
        if tag_num != None:
            number = tag_num.text
            if number in downloaded_numbers:
                logger.info(f"{number} already downloaded or in xlsx, skip.")
                continue
            logger.info(f"get {number} from {detail_url}")
        else:
            logger.error(f"no number in {detail_url}")
            continue

        detail_url = urljoin(baseurl, detail_url)
        data = get_data(detail_url,Javdb(session))
        logger.info(f"{data['number']} loaded.")
        down_img(img_dir, data)
        wdata = cover_wdata(data)
        sheet.append(wdata)
        sleep()
    
    return datalen

def test():
    session = httprequest.request_session(cookies=Javdb.get_cookies())
    data = get_data('https://javdb459.com/v/Rkdx08',Javdb(session))
    wdata = cover_wdata(data)


def other(baseurl:str, tree:etree._Element, img_dir:str, pageAt:int, sheet:openpyxl.worksheet.worksheet.Worksheet, session):

    detail_urls = tree.xpath('//*[contains(@class,"movie-list")]/div/a/@href')
    if len(detail_urls) == 0 :
        detail_urls = tree.xpath('//*[contains(@class,"movie-list")]/div/div/a/@href')
    datalen = len(detail_urls)
    logger.info(f"get {datalen} urls in page {pageAt}")

    for detail_url in detail_urls:
        if exit_now:
            break    
        detail_url = urljoin(baseurl, detail_url)
        
        data = get_data(detail_url,Javdb(session))
        logger.info(f"{data['number']} loaded.")
        if data['number'] in downloaded_numbers:
            continue
        
        down_img(img_dir, data)
        wdata = cover_wdata(data)
        sheet.append(wdata)
        sleep()
    
    return datalen
    

def get_data(detail_url:str,parser=None):
    json_data = parser.get_from_detail_url(detail_url)
    if not json_data:
        logger.info(f"{detail_url} load error.")
        return None
    return cover_json_data(json.loads(json_data))

def down_img(img_dir:str,data:dict):
    try:
        if img_dir is not None:
            httprequest.download(data['cover'],os.path.join(img_dir, data['number'] + functions.image_ext(data['cover'])))
    except Exception as e:
        logger.error("download img error. "+data['cover'])

def cover_wdata(data:dict):
    best = getBestMagnet(data["magnets"])
    wdata = []
    for index, key in enumerate(columns):
        if "magnet" in key:
            if "" == best:
                wdata.append("")
            else:
                if key == "magnet_link":
                    wdata.append(best["link"])
                elif key == "magnet_meta":
                    wdata.append(best["meta"])
                elif key == "magnet_tags":
                    wdata.append(",".join(best["tags"]))
        else:
            wdata.append(data[key])
    return wdata


def getBestMagnet(arr):
    if len(arr) == 0:
        return ""
    result = None
    sc = 0
    for item in arr:
        scope = 0
        if '字幕' in item["tags"]:
            scope += 100

        if "1個文件" in item["meta"]:
            scope += 4

        try:
            size = None
            _re = re.search(r'([\d\.]*)(?=GB)',item["meta"])
            if _re is None:
                _re = re.search(r'([\d\.]*)(?=MB)',item["meta"])
                if _re is not None:
                    size  = float(_re.group(0))/1000
            else:
                size  = float(_re.group(0))         

            if size is not None:
                scope += size if size < 8 else 8   
        except Exception as e:
            logger.error(f"get Magnet link size error. {item} {e}")

        if scope > sc or result is None:
            sc = scope
            result = item
    return result

def sleep():
    interval = config.getIntValue("common.interval")
    if interval != 0:
        logger.info(f"Continue in {interval} seconds")
        time.sleep(interval)
    return interval