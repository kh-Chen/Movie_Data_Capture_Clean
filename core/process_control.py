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
    
    # 指定番号查询信息  ---------------------------------
    search_for_number = config.getStrValAtArgs("search_for_number")
    if search_for_number != '':
        logger.info(f"Find --search in the parameter list. value is [{search_for_number}]. run in search mode!")
        from . import mode_search
        mode_search.run(search_for_number)
        return
    
    # TODO 指定文件刮削 ---------------------------------

    # 检查配置文件参数合法性    --------------------------
    main_mode = config.getIntValue("common.main_mode")
    logger.debug(f"common.main_mode [{main_mode}]")
    if main_mode not in (1, 2, 3):
        logger.error(f"Main mode must be 1 or 2 or 3! ")
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
