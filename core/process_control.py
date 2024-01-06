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
    
    # 运行自动评分模式  -------------------------------------
    if config.getBoolValAtArgs("rate_mode"):
        logger.info(f"Find --rate in the parameter list. ")
        from . import mode_autorate
        mode_autorate.run()
        return
    
    # 指定番号查询信息  ---------------------------------
    search_for_number = config.getStrValAtArgs("search_for_number")
    if search_for_number != '':
        logger.info(f"Find --search in the parameter list. value is [{search_for_number}]. run in search mode!")
        from . import mode_search
        mode_search.run(search_for_number)
        return
    
    # 指定文件刮削 ---------------------------------
    specify_file = config.getStrValAtArgs("specify_file")
    if specify_file != '':
        logger.info(f"Find --specify-file in the parameter list. value is [{specify_file}]. run in specify-file mode!")
        from . import mode_normal
        config.setStrValAtConf("common.failed_output_folder", os.path.dirname(specify_file))
        config.setStrValAtConf("common.success_output_folder", os.path.dirname(specify_file))
        mode_normal.do_capture_with_single_file(specify_file)
        return

    # 爬取指定url   -------------------------------------
    scraping_url = config.getOriginalValAtArgs("scraping_url")
    if scraping_url is not None and len(scraping_url) != 0:
        with_cover = config.getOriginalValAtArgs("with_cover")
        logger.info(f"Find --spider-url in the parameter list. value is [{scraping_url}]. with_cover flag is [{with_cover}]. run in scraping mode!")
        from . import mode_url_scraper
        mode_url_scraper.run(scraping_url,with_cover)
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
