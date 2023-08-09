import os
import sys
import time
import signal
from unicodedata import category

import logger
import config
import core.scraper as scraper

def signal_handler(*args):
    logger.info("Ctrl+C detected, Exit.")
    os._exit(0)

def start():
    logger.debug("process_control start.")
    
    # signal.signal(signal.SIGINT, signal_handler)

    #---------------------------------------------------
    search_for_number = config.getStrValAtArgs("search_for_number")
    if search_for_number != '':
        logger.info(f"Find --search in the parameter list. value is [{search_for_number}]. run in search mode!")
        search_mode(search_for_number)
        return
    #---------------------------------------------------


    # main_mode = config.getIntValue("common.main_mode")
    # logger.debug(f"common.main_mode [{main_mode}]")
    # if main_mode not in (1, 2, 3):
    #     logger.error(f"Main mode must be 1 or 2 or 3! ")
    #     return 
    
    #TODO 检查更新
    #TODO 再运行延迟
    # create_failed_folder()
    # if not os.path.exists(failed_folder):
    #     try:
    #         os.makedirs(failed_folder)
    #     except:
    #         print(f"[-]Fatal error! Can not make folder '{failed_folder}'")
    #         os._exit(0)

def search_mode(numbers:str):
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

def cn_space(v: str, n: int) -> int:
    return n - [category(c) for c in v].count('Lo')


    