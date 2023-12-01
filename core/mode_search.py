import time

import logger
import config
from . import scraper
from utils.functions import cn_space

def run(numbers:str):
    number_arr = numbers.split(",")
    for number in number_arr:
        json_data = scraper.get_base_data_by_number(number)
        logger.info(f"json data for number [{number}]: ")
        print_data(json_data)
        interval = config.getIntValue("common.interval")
        if interval != 0:
            logger.info(f"Continue in {interval} seconds")
            time.sleep(interval)

def print_data(json_data):
    try:
        logger.info("-------- INFO -------")
        for i, v in json_data.items():
            if i == 'magnets' and len(v) > 0:
                for d in v:
                    logger.info(f'{i:<{cn_space(i, 14)}}: {d["link"]:<{cn_space(d["link"], 100)}}{d["meta"]:<{cn_space(d["meta"], 15)}} {d["tags"]}')
            else:
                logger.info(f'{i:<{cn_space(i, 14)}}: {v}')

        logger.info("-------- INFO -------")
    except:
        logger.error("print_data error.")