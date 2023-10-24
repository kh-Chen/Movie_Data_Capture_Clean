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

columns  = ["number","title","actor","userrating","uservotes","release"]
title    = ["番号",  "标题",  "演员", "评分",      "人数",      "发布日期"]

def run(arr:list):
    url = arr[0]
    file = arr[1] if len(arr) > 1 else "scrapingurl.xlsx"
    logger.info(f"scraping data from [{url}] save to [{file}]...")
    session = httprequest.request_session()
    javdb(url, file, session)

#url中存在page参数时只拉取本页数据，不含page参数时则自动翻页拉取全部数据
def javdb(url:str, file:str, session) : 
    from .scrapinglib.custom.javdb import Javdb
    interval = config.getIntValue("common.interval")

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
                row += 1
                for index, key in enumerate(columns):
                    sheet.write(row, index, data[key])
                
                if interval != 0:
                    logger.info(f"Continue in {interval} seconds")
                    time.sleep(interval)
            if not getOtherPage or len(detail_urls) != 40:
                break
            pageAt += 1
            url = url + '&page=' + str(pageAt)
    except Exception as e:
        logger.error(f"url scraper error. {e}")
        logger.error(f"{traceback.format_exc()}")
    xlsx.close()