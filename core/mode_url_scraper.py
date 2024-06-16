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


from lxml import etree
import xlsxwriter

columns  = ["number","title","actor","userrating","uservotes","release","magnet_link","magnet_meta","magnet_tags",]
title    = ["番号",  "标题",  "演员", "评分",      "人数",      "发布日期","磁力",       "内容",        "标签"]
downloaded_numbers = []

exit_now = False
def SIGINT_callback():
    global exit_now
    exit_now = True
    logger.info(f"SIGINT_callback: exit_now={exit_now}")
    
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
    
    img_dir = None
    if with_cover:
        img_dir = xlsxfile + "_cover"
        functions.create_folder(img_dir)
        logger.info(f"scraping data from [{url}] save to [{xlsxfile}] img download to [{img_dir}]")

    javdb(url, xlsxfile, img_dir)

#url中存在page参数时只拉取本页数据，不含page参数时则自动翻页拉取全部数据
def javdb(url:str, file:str, img_dir:str) : 
    from .scrapinglib.custom.javdb import Javdb
    interval = config.getIntValue("common.interval")
    session = httprequest.request_session(cookies=Javdb.get_cookies())
    xlsx = xlsxwriter.Workbook(file)
    sheet = xlsx.add_worksheet('Sheet1')

    try:
        row = 0
        for index, _title in enumerate(title):
            sheet.write(row, index, _title)

        getOtherPage = 'page=' not in url
        pageAt = 1
        while True:
            if exit_now:
                break    
            resp = session.get(url)
            tree = etree.fromstring(resp.text, etree.HTMLParser()) 
            detail_urls = tree.xpath('//*[contains(@class,"movie-list")]/div/a/@href')
            if len(detail_urls) == 0 :
                detail_urls = tree.xpath('//*[contains(@class,"movie-list")]/div/div/a/@href')
            logger.info(f"get {len(detail_urls)} urls in page {pageAt}")
            for detail_url in detail_urls:
                if exit_now:
                    break    
                detail_url = urljoin(resp.url, detail_url)
                parser = Javdb(session)
                json_data = parser.get_from_detail_url(detail_url)
                if not json_data:
                    logger.info(f"{detail_url} load error.")
                    continue
                data = cover_json_data(json.loads(json_data))
                # print_data(data)
                logger.info(f"{data['number']} loaded.")
                if data['number'] in downloaded_numbers:
                    continue
                try:
                    if img_dir is not None:
                        httprequest.download(data['cover'],os.path.join(img_dir, data['number'] + functions.image_ext(data['cover'])))
                except Exception as e:
                    logger.error("download img error. "+data['cover'])

                best = getBestMagnet(data["magnets"])
                row += 1
                for index, key in enumerate(columns):
                    if "magnet" in key:
                        if "" == best:
                            sheet.write(row, index, "")
                        else:
                            if key == "magnet_link":
                                sheet.write(row, index, best["link"])
                            elif key == "magnet_meta":
                                sheet.write(row, index, best["meta"])
                            elif key == "magnet_tags":
                                sheet.write(row, index, ",".join(best["tags"]))
                    else:
                        sheet.write(row, index, data[key])
                
                if interval != 0:
                    logger.info(f"Continue in {interval} seconds")
                    time.sleep(interval)
            if not getOtherPage or len(detail_urls) < 20:
                break
            pageAt += 1
            url = url + ('&' if "?" in url else '?') + 'page=' + str(pageAt)
            
    except Exception as e:
        logger.error(f"url scraper error. {e}")
        logger.error(f"{traceback.format_exc()}")
    xlsx.close()

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

        if scope > sc:
            sc = scope
            result = item
    return result
