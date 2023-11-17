import os
import re
import sys
import time
import typing
import signal

from pathlib import Path
import logger
import config



def start():
    logger.debug("process_control start.")
    # TODO 检查更新 ------------------------------------

    # 运行调试脚本  -------------------------------------
    if config.getBoolValAtArgs("test_mode"):
        logger.info(f"Find --test in the parameter list. ")
        from . import mode_test
        mode_test.run()
        return
    
    # 指定番号查询信息  ---------------------------------
    search_for_number = config.getStrValAtArgs("search_for_number")
    if search_for_number != '':
        logger.info(f"Find --search in the parameter list. value is [{search_for_number}]. run in search mode!")
        from . import mode_search
        mode_search.run(search_for_number)
        return
    
    # TODO 指定文件刮削 ---------------------------------

    # 爬取指定url   -------------------------------------
    scraping_url = config.getOriginalValAtArgs("scraping_url")
    if scraping_url is not None and len(scraping_url) != 0:
        logger.info(f"Find --spider-url in the parameter list. value is [{scraping_url}]. run in scraping mode!")
        from . import mode_url_scraper
        mode_url_scraper.run(scraping_url)
        return

    # 根据配置寻找将会刮削的所有视频    -------------------
    if config.getBoolValAtArgs("list_movie"):
        logger.info(f"Find --list-movie in the parameter list. Find movies by config file and print it.")
        from . import mode_list_movie
        mode_list_movie.run()
        return
    
    # 默认模式  -----------------------------------------
    logger.info(f"run in default mode. ")
    from . import mode_normal
    mode_normal.run()
    return
