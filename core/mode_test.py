from utils import httprequest
import requests
from lxml import etree
import os
import shutil
import json
import translators as ts
import config
from urllib.parse import urljoin
from .scraper import cover_json_data
from .scrapinglib.custom.javdb import Javdb
from .mode_list_movie import movie_lists
from .mode_url_scraper import getBestMagnet

def run():
    print("test mode")
        