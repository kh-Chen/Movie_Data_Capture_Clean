from utils import httprequest
import requests
from lxml import etree
import os
import shutil
import json
from urllib.parse import urljoin
from .scraper import cover_json_data
from .scrapinglib.custom.javdb import Javdb
from .mode_list_movie import movie_lists
from .mode_url_scraper import getBestMagnet

G_USER_AGENT = r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.133 Safari/537.36'

def run():
    javdb("https://javdb523.com/users/watched_videos")

def javdb(url:str) : 
    
    movie_list = movie_lists()
    map = {}
    for _p in movie_list:
        key = os.path.basename(_p).split(" ")[0]
        map[key] = _p
    

    session = httprequest.request_session(cookies=Javdb._cookies)
    
    getOtherPage = 'page=' not in url
    pageAt = 1
    while True:
        resp = session.get(url)

        tree = etree.fromstring(resp.text, etree.HTMLParser()) 
        detail_urls = tree.xpath('//*[contains(@class,"movie-list")]/div/div/a/@href')
        
        for detail_url in detail_urls:
            _key = detail_url.split('/')[-1]
            # filepath = "" if _key not in map else map[_key] 
            # print(_key,filepath)

            if _key not in map:
                detail_url = urljoin(resp.url, detail_url)
                parser = Javdb(session)
                json_data = parser.get_from_detail_url(detail_url)
                if not json_data:
                    print(f"{detail_url} load error.")
                    continue
                data = cover_json_data(json.loads(json_data))
                print(data["number"],data["actor"],data["title"])
            
            # if filepath != "":
            #     newfilepath = f"/mnt/f/downloaded/1/{os.path.basename(filepath)}"
            #     print(filepath, "->", newfilepath)
            #     shutil.move(filepath,  newfilepath)

        
        if not getOtherPage or len(detail_urls) < 20:
            break   
        pageAt += 1
        url = url + ('&' if "?" in url else '?') + 'page=' + str(pageAt)
        