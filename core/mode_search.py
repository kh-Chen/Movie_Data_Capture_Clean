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
                # if i == 'outline':
                #     logger.info(f'{"%-19s" % i} : {len(v)} characters')
                #     continue
                # if i == 'actor_photo' or i == 'year':
                #     continue
                # if i == 'extrafanart':
                #     logger.info(f'{"%-19s" % i} : {len(v)} links')
                #     continue
                logger.info(f'{i:<{cn_space(i, 19)}} : {v}')

            logger.info("-------- INFO -------")
        except:
            pass
        #TODO 自定义睡眠时间
        time.sleep(1)