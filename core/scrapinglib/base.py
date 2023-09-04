import re
import json
import importlib
import traceback
from logging import Logger

from .parser import Parser
import logger
import config

class Scraper:

    adult_full_sources = [
        'javlibrary', 'javdb', 'javbus', 'airav', 'fanza', 'xcity', 'jav321',
        'mgstage', 'fc2', 'avsox', 'dlsite', 'carib', 'madou', 'msin',
        'getchu', 'gcolle', 'javday', 'pissplay', 'javmenu', 'pcolle', 'caribpr'
    ]

    def __init__(self):
        pass

    def search(self, number):
        available_sources = config.getStrValue("capture.data_source")
        sources = self.checkAdultSources(number, available_sources)
        json_data= {}
        for source in sources:
            logger.debug(f'using source [{source}]')
            try:
                module = importlib.import_module('.' + source, 'core.scrapinglib.custom')
                parser_type = getattr(module, source.capitalize())
                parser: Parser = parser_type()
                data = parser.search(number)
                if data == 404:
                    continue
                json_data = json.loads(data)
            except Exception as e:
                logger.error(f"scrape [{number}] from [{source}] error. info: {e}")
                logger.debug(f"{traceback.format_exc()}")
            
            if self.get_data_state(json_data):
                logger.debug(f"Find movie [{number}] metadata on website '{source}' success.")
                break
        
        # TODO javdb的封面有水印，如果可以用其他源的封面来替换javdb的封面
        if not json_data or json_data['title'] == "":
            return None
        
        if len(json_data['actor']) == 0:
            json_data['actor'] = "Anonymous"
                
        return json_data
        

    def checkAdultSources(self, file_number, str_sources ):
        if not str_sources:
            sources = self.adult_full_sources
        else:
            sources = str_sources.split(',')

        def insert(sources, source):
            if source in sources:
                sources.insert(0, sources.pop(sources.index(source)))
            return sources

        if len(sources) <= len(self.adult_full_sources):
            # if the input file name matches certain rules,
            # move some web service to the beginning of the list
            lo_file_number = file_number.lower()
            if "carib" in sources:
                sources = insert(sources, "caribpr")
                sources = insert(sources, "carib")
            elif "item" in file_number or "GETCHU" in file_number.upper():
                sources = ["getchu"]
            elif "rj" in lo_file_number or "vj" in lo_file_number:
                sources = ["dlsite"]
            elif re.search(r"[\u3040-\u309F\u30A0-\u30FF]+", file_number):
                sources = ["dlsite", "getchu"]
            elif "pcolle" in sources and "pcolle" in lo_file_number:
                sources = ["pcolle"]
            elif "fc2" in lo_file_number:
                sources = ["fc2", "avsox", "msin"]
            elif (re.search(r"\d+\D+-", file_number) or "siro" in lo_file_number):
                if "mgstage" in sources:
                    sources = insert(sources, "mgstage")
            elif "gcolle" in sources and (re.search("\d{6}", file_number)):
                sources = insert(sources, "gcolle")
            elif re.search(r"^\d{5,}", file_number) or \
                    (re.search(r"^\d{6}-\d{3}", file_number)) or "heyzo" in lo_file_number:
                sources = ["avsox", "carib", "caribpr", "javbus", "xcity", "javdb"]
            elif re.search(r"^[a-z0-9]{3,}$", lo_file_number):
                if "xcity" in sources:
                    sources = insert(sources, "xcity")
                if "madou" in sources:
                    sources = insert(sources, "madou")

        # check sources in func_mapping
        todel = []
        for s in sources:
            if not s in self.adult_full_sources:
                todel.append(s)
        if len(todel) != 0: 
            logger.info(f'Source Not Exist , auto remove: {todel}')
            return list(set(sources)-set(todel))
        else:
            return sources
            
    

    def get_data_state(self, data: dict) -> bool:  # 元数据获取失败检测
        if "title" not in data or "number" not in data :
            return False
        if data["title"] is None or data["title"] == "" or data["title"] == "null":
            return False
        if data["number"] is None or data["number"] == "" or data["number"] == "null":
            return False
        return True