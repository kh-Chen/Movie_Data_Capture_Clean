from .scrapinglib.base import Scraper
import logger
import config

def get_base_data_by_number(number:str):
    logger.debug(f"get Data for number [{number}]...")
    sc = Scraper()
    return sc.search(number)