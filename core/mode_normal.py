import re,os,time
import typing
from pathlib import Path

import logger
import config
from config import constant
from . import mode_list_movie
from . import scraper
from utils.number_parser import get_number
from utils.functions import create_folder


def run():
    failed_folder = config.getStrValue("common.failed_output_folder")
    success_folder = config.getStrValue("common.success_output_folder")
    create_folder(failed_folder)
    create_folder(success_folder)

    stop_count = config.getIntValue("common.stop_counter")

    movie_list = mode_list_movie.movie_lists()
    print(f'Find {len(movie_list)} movies. stop_counter[{stop_count}]')

    count_all = len(movie_list) if stop_count == 0 else min(len(movie_list), stop_count)

    for movie_path in movie_list: 
        count = count + 1
        percentage = str(count / int(count_all) * 100)[:4] + '%'
        logger.info(f"running {percentage} [{count}/{count_all}]")
        do_capture_with_single_file(movie_path)
        if count >= stop_count:
            logger.info("Stop counter triggered!")
            break
        time.sleep(1)


def do_capture_with_single_file(movie_path: str, spec_number:str=None):
    
    number = spec_number if spec_number is not None else get_number(os.path.basename(movie_path))
    movie_path = os.path.abspath(movie_path)
    logger.info(f"[{number}] As Number Processing for '{movie_path}'")

    if number is None:
        logger.error("number empty ERROR.")
        moveFailedFolder(movie_path)
        return
    
    json_data = scraper.get_base_data_by_number(number)
    if json_data is None:
        moveFailedFolder(movie_path)
        return
    
    if json_data["number"] != number:
        number = json_data["number"]
        
        
        

def moveFailedFolder(movie_path):
    pass