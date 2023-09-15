import time
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


def javdb(url:str, file:str, session) : 
    from .scrapinglib.custom.javdb import Javdb

    resp = session.get(url)
    tree = etree.fromstring(resp.text, etree.HTMLParser()) 
    detail_urls = tree.xpath('//*[contains(@class,"movie-list")]/div/a/@href')

    if len(detail_urls) == 0:
        return
    logger.info(f"get {len(detail_urls)} urls")

    xlsx = xlsxwriter.Workbook(file)
    sheet = xlsx.add_worksheet('Sheet1')
    row = 0
    for index, _title in enumerate(title):
        sheet.write(row, index, _title)

    for detail_url in detail_urls:
        detail_url = urljoin(resp.url, detail_url)
        parser = Javdb(session)
        json_data = parser.get_from_detail_url(detail_url)
        data = cover_json_data(json.loads(json_data))
        row += 1
        for index, key in enumerate(columns):
            sheet.write(row, index, data[key])
        logger.info(f"{data['number']} loaded.")
        interval = config.getIntValue("common.interval")
        if interval != 0:
            logger.info(f"Continue in {interval} seconds")
            time.sleep(interval)
        
    xlsx.close()

