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
        try:
            logger.info("-------- INFO -------")
            for i, v in json_data.items():
                logger.info(f'{i:<{cn_space(i, 19)}} : {v}')

            logger.info("-------- INFO -------")
        except:
            pass
        interval = config.getIntValue("common.interval")
        if interval != 0:
            logger.info(f"Continue in {interval} seconds")
            time.sleep(interval)