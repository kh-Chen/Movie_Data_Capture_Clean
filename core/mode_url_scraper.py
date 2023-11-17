import re
import time
import traceback
from urllib.parse import urljoin
import json

import logger
import config
from .scraper import cover_json_data
from utils import httprequest

from lxml import etree
import xlsxwriter

columns  = ["number","title","actor","userrating","uservotes","release","magnet_link","magnet_meta","magnet_tags",]
title    = ["番号",  "标题",  "演员", "评分",      "人数",      "发布日期","磁力",       "内容",        "标签"]

def run(arr:list):
    url = arr[0]
    file = arr[1] if len(arr) > 1 else "scrapingurl.xlsx"
    logger.info(f"scraping data from [{url}] save to [{file}]...")
    javdb(url, file)

#url中存在page参数时只拉取本页数据，不含page参数时则自动翻页拉取全部数据
def javdb(url:str, file:str) : 
    from .scrapinglib.custom.javdb import Javdb
    interval = config.getIntValue("common.interval")
    session = httprequest.request_session(cookies=Javdb._cookies)
    xlsx = xlsxwriter.Workbook(file)
    sheet = xlsx.add_worksheet('Sheet1')

    try:
        row = 0
        for index, _title in enumerate(title):
            sheet.write(row, index, _title)

        getOtherPage = 'page=' not in url
        pageAt = 1
        while True:
            resp = session.get(url)
            tree = etree.fromstring(resp.text, etree.HTMLParser()) 
            detail_urls = tree.xpath('//*[contains(@class,"movie-list")]/div/a/@href')
            if len(detail_urls) == 0 :
                detail_urls = tree.xpath('//*[contains(@class,"movie-list")]/div/div/a/@href')
            logger.info(f"get {len(detail_urls)} urls in page {pageAt}")
            for detail_url in detail_urls:
                detail_url = urljoin(resp.url, detail_url)
                parser = Javdb(session)
                json_data = parser.get_from_detail_url(detail_url)
                if not json_data:
                    logger.info(f"{detail_url} load error.")
                    continue
                data = cover_json_data(json.loads(json_data))
                logger.info(f"{data['number']} loaded.")

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
                                sheet.write(row, index, "".join(best["tags"]))
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
        scope += len(item["tags"])*10
        if "1個文件" in item["meta"]:
            scope += 9
        size = re.search(r'([\d\.]*)(?=GB)',item["meta"]).group(0)
        if size is not None:
            scope += float(size)
        if scope > sc:
            sc = scope
            result = item
    return result
