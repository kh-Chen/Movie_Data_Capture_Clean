from .scrapinglib.base import Scraper
import logger
import config

def get_base_data_by_number(number:str):
    logger.debug(f"get Data for number [{number}]...")

    switch = config.getBoolValue("proxy.switch")
    url = config.getStrValue("proxy.url")
    timeout = config.getStrValue("proxy.timeout")
    retry = config.getStrValue("proxy.retry")
    cacert_file = config.getStrValue("proxy.cacert_file")
    website = config.getStrValue("priority.website")

    sc = Scraper(logger.get_real_logger())
    sc.set_morestoryline(False)
    logger.debug(f"proxy.switch value[{switch}]")
    if switch:
        sc.set_proxies({'http':url, 'https':url})
    
    return sc.search(number,website)