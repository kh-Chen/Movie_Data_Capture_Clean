import json
import os
import re
import time
import secrets
import builtins

from urllib.parse import urljoin
from lxml.html import fromstring
from multiprocessing.dummy import Pool as ThreadPool

from utils.httprequest import get_html_by_form, get_html_by_scraper, request_session
import logger
import config

# 舍弃 Amazon 源
G_registered_storyline_site = {"airav", "avno1", "58avgo"}

G_mode_txt = ('顺序执行','线程池')
def is_japanese(raw: str) -> bool:
    """
    日语简单检测
    """
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\uFF66-\uFF9F]', raw, re.UNICODE))

class noThread(object):
    def map(self, fn, param):
        return list(builtins.map(fn, param))
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# 获取剧情介绍 从列表中的站点同时查，取值优先级从前到后
def getStoryline(number, uncensored=None):
    storyline_switch = config.getBoolValue("capture.get_storyline_switch")
    if not storyline_switch:
        return ""

    storyline_sites = config.getStrValue("capture.storyline_data_source").split(",")
    start_time = time.time()
    sort_sites = []
    for s in storyline_sites:
        if s in G_registered_storyline_site:
            sort_sites.append(s)

    mp_args = ((site, number) for site in sort_sites)   
    run_mode = config.getIntValue("capture.storyline_run_mode")
    with ThreadPool(len(sort_sites)) if run_mode > 0 else noThread() as pool:
        results = pool.map(getStoryline_mp, mp_args)
    
    logger.debug(f"Storyline run with mode[{run_mode}] site count [{len(sort_sites)}] used time {time.time() - start_time:.3f}s")
    
    sel_site = ''
    sel = ''
    # logger.debug(f"{results}")
    for site, desc in zip(sort_sites, results):
        if isinstance(desc, str) and len(desc):
            if not is_japanese(desc):
                sel_site, sel = site, desc
                break
            if not len(sel_site):
                sel_site, sel = site, desc
        
    logger.debug(f"selected site [{sel_site}], len [{len(sel) if isinstance(sel, str) else 0}]")
    return sel


def getStoryline_mp(args):
    (site, number) = args
    start_time = time.time()
    storyline = None
    if not isinstance(site, str):
        return storyline
    elif site == "airav":
        storyline = getStoryline_airav(number)
    elif site == "avno1":
        storyline = getStoryline_avno1(number)
    elif site == "58avgo":
        storyline = getStoryline_58avgo(number)
    
    logger.debug(f"Storyline thread site [{site}] used time {time.time() - start_time:.3f}s result len [{len(storyline) if isinstance(storyline, str) else 0}]")
    return storyline


def getStoryline_airav(number):
    try:
        site = secrets.choice(('airav.cc','airav4.club'))
        url = f'https://{site}/searchresults.aspx?type=0&Search={number}'
        session = request_session()
        res = session.get(url)
        if not res:
            raise ValueError(f"get_html_by_session('{url}') failed")
        lx = fromstring(res.text)
        urls = lx.xpath('//div[@id="testHcsticky"]/div/ul/li/div/a[@class="ga_click"]/@href')
        txts = lx.xpath('//div[@id="testHcsticky"]/div/ul/li/div/a[@class="ga_click"]/h3[@class="one_name ga_name"]/text()')
        detail_url = None
        for txt, url in zip(txts, urls):
            logger.info(f"Storyline found: {txt}")
            if re.search("馬賽克破", txt):
                continue
            if re.search(number, txt, re.I):
                detail_url = urljoin(res.url, url)
                break
        if detail_url is None:
            raise ValueError("number not found")
        res = session.get(detail_url)
        if not res.ok:
            raise ValueError(f"session.get('{detail_url}') failed")
        lx = fromstring(res.text)
        t = str(lx.xpath('/html/head/title/text()')[0]).strip()
        airav_number = str(re.findall(r'^\s*\[(.*?)]', t)[0])
        if not re.search(number, airav_number, re.I):
            raise ValueError(f"page number ->[{airav_number}] not match")
        d1 = str(lx.xpath('//span[@itemprop="description"]/text()')[0])
        logger.debug(f"Storyline description: {d1}")
        desc = str(lx.xpath('//span[@itemprop="description"]/text()')[0]).strip()
        return desc
    except Exception as e:
        logger.debug(f"MP getStoryline_airav Error: {e},number [{number}].")
        
    return None


def getStoryline_58avgo(number):
    try:
        url = 'http://58avgo.com/cn/index.aspx' + secrets.choice([
                '', '?status=3', '?status=4', '?status=7', '?status=9', '?status=10', '?status=11', '?status=12',
                '?status=1&Sort=Playon', '?status=1&Sort=dateupload', 'status=1&Sort=dateproduce'
        ]) # 随机选一个，避免网站httpd日志中单个ip的请求太过单一
        kwd = number[:6] if re.match(r'\d{6}[\-_]\d{2,3}', number) else number
        result, browser = get_html_by_form(url, fields = {'ctl00$TextBox_SearchKeyWord' : kwd}, return_type = 'browser')
        if not result:
            raise ValueError(f"get_html_by_form('{url}','{number}') failed")
        if f'searchresults.aspx?Search={kwd}' not in browser.url:
            raise ValueError("number not found")
        s = browser.page.select('div.resultcontent > ul > li.listItem > div.one-info-panel.one > a.ga_click')
        link = None
        for a in s:
            title = a.h3.text.strip()
            list_number = title[title.rfind(' ')+1:].strip()
            if re.search(number, list_number, re.I):
                link = a
                break
        if link is None:
            raise ValueError("number not found")
        result = browser.follow_link(link)
        if not result.ok or 'playon.aspx' not in browser.url:
            raise ValueError("detail page not found")
        title = browser.page.select_one('head > title').text.strip()
        detail_number = str(re.findall('\[(.*?)]', title)[0])
        if not re.search(number, detail_number, re.I):
            raise ValueError(f"detail page number not match, got ->[{detail_number}]")
        return browser.page.select_one('#ContentPlaceHolder1_Label2').text.strip()
    except Exception as e:
        logger.debug(f"MP getOutline_58avgo Error: {e}, number [{number}].")
        pass
    return ''


def getStoryline_avno1(number):  #获取剧情介绍 从avno1.cc取得
    try:
        site = secrets.choice(['1768av.club','2nine.net','av999.tv','avno1.cc',
            'hotav.biz','iqq2.xyz','javhq.tv',
            'www.hdsex.cc','www.porn18.cc','www.xxx18.cc',])
        url = f'http://{site}/cn/search.php?kw_type=key&kw={number}'
        lx = fromstring(get_html_by_scraper(url))
        descs = lx.xpath('//div[@class="type_movie"]/div/ul/li/div/@data-description')
        titles = lx.xpath('//div[@class="type_movie"]/div/ul/li/div/a/h3/text()')
        if not descs or not len(descs):
            raise ValueError(f"number not found")
        partial_num = bool(re.match(r'\d{6}[\-_]\d{2,3}', number))
        for title, desc in zip(titles, descs):
            page_number = title[title.rfind(' ')+1:].strip()
            if not partial_num:
                # 不选择title中带破坏版的简介
                if re.match(f'^{number}$', page_number, re.I) and title.rfind('破坏版')== -1:
                    return desc.strip()
            elif re.search(number, page_number, re.I):
                return desc.strip()
        raise ValueError(f"page number ->[{page_number}] not match")
    except Exception as e:
        logger.debug(f"MP getOutline_avno1 Error: {e}, number [{number}].")
        pass
    return ''

