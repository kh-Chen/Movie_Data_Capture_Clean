import time

import logger
import config
from . import scraper
from utils.functions import cn_space

def run(numbers:str):
    number_arr = numbers.split(",")
    for number in number_arr:
        json_data = scraper.get_base_data_by_number(number)
        logger.debug(f"json data for number [{number}]: ")
        try:
            logger.debug("-------- INFO -------")
            for i, v in json_data.items():
                if i == 'outline':
                    logger.debug(f'{"%-19s" % i} : {len(v)} characters')
                    continue
                if i == 'actor_photo' or i == 'year':
                    continue
                if i == 'extrafanart':
                    logger.debug(f'{"%-19s" % i} : {len(v)} links')
                    continue
                logger.debug(f'{i:<{cn_space(i, 19)}} : {v}')

            logger.debug("-------- INFO -------")
        except:
            pass
        #TODO 自定义睡眠时间
        time.sleep(1)