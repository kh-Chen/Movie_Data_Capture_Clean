import re,os,time
import typing
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import shutil

import logger
import config
from config import constant
from . import mode_list_movie
from . import scraper
from utils.number_parser import get_number
from utils.functions import create_folder,escape_path,image_ext,file_not_exist_or_empty
from utils.httprequest import download


def run():
    failed_folder = config.getStrValue("common.failed_output_folder")
    success_folder = config.getStrValue("common.success_output_folder")
    create_folder(failed_folder)
    create_folder(success_folder)

    stop_count = config.getIntValue("common.stop_counter")

    movie_list = mode_list_movie.movie_lists()
    logger.info(f'Find {len(movie_list)} movies. stop_counter[{stop_count}]')

    count_all = len(movie_list) if stop_count == 0 else min(len(movie_list), stop_count)
    processed = 0
    for movie_path in movie_list: 
        processed = processed + 1
        percentage = str(processed / int(count_all) * 100)[:4] + '%'
        logger.info(f"running {percentage} [{processed}/{count_all}]")
        do_capture_with_single_file(movie_path)
        if processed >= count_all:
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
    
    main_mode = config.getIntValue("common.main_mode")
    if main_mode == 1:
        main_mode_1(movie_path, json_data)
    elif main_mode == 2:
        pass
    elif main_mode == 3:
        pass


def main_mode_1(movie_path, json_data):
    number = json_data["number"]

    movie_target_dir = create_movie_folder_by_rule(json_data)
    if movie_target_dir is None:
        moveFailedFolder(movie_path)
        return
    
    cn_sub = False
    if re.search(r'[-_]C(\.\w+$|-\w+)|\d+ch(\.\w+$|-\w+)', movie_path,
                 re.I) or '中文' in movie_path or '字幕' in movie_path:
        cn_sub = True
    
    # 处理封面
    if "cover" in json_data and json_data["cover"] != '':
        cover_url = json_data["cover"]
        ext = image_ext(cover_url)
        fanart_path = f"fanart{ext}"
        poster_path = f"poster{ext}"
        thumb_path = f"thumb{ext}"
        if config.getBoolValue("Name_Rule.image_naming_with_number"):
            fanart_path = f"{number}{'-C' if cn_sub else ''}-fanart{ext}"
            poster_path = f"{number}{'-C' if cn_sub else ''}-poster{ext}"
            thumb_path = f"{number}{'-C' if cn_sub else ''}-thumb{ext}"
        
        full_filepath = os.path.join(movie_target_dir, thumb_path)
        succ = image_download(cover_url, full_filepath)
        shutil.copyfile(full_filepath, os.path.join(movie_target_dir, poster_path))
        if succ and not config.getBoolValue("common.jellyfin"):
            shutil.copyfile(full_filepath, os.path.join(movie_target_dir, fanart_path))
            # TODO cutImage(imagecut, path, thumb_path, poster_path, bool(conf.face_uncensored_only() and not uncensored))

     # 下载预告片
        # if conf.is_trailer() and json_data.get('trailer'):
        #     trailer_download(json_data.get('trailer'), leak_word, c_word, hack_word, number, path, movie_path)

    # 下载剧照
    if config.getBoolValue("extrafanart.switch") and "extrafanart" in json_data and len(json_data.get('extrafanart')) > 0:
        extrafanart_download(json_data.get('extrafanart'), movie_target_dir)
                

    # 下载演员头像 KODI .actors 目录位置
    # if conf.download_actor_photo_for_kodi():
    #     actor_photo_download(json_data.get('actor_photo'), path, number)
    
    # TODO link mode
    shutil.move(movie_path, os.path.join(movie_target_dir,f"{number}{'-C' if cn_sub else ''}{os.path.splitext(movie_path)[-1]}"))




def moveFailedFolder(movie_path):
    pass


def create_movie_folder_by_rule(json_data):
    location_rule = config.getStrValue("Name_Rule.location_rule")
    actor = json_data.get('actor')
    if 'actor' in location_rule and len(actor) > 100:
        location_rule = location_rule.replace("actor", "'多人作品'")

    maxlen = config.getStrValue("Name_Rule.max_title_len")
    if 'title' in location_rule and len(json_data["title"]) > maxlen:
        shorttitle = json_data["title"][0:maxlen]
        location_rule = location_rule.replace("title", f"'{shorttitle}'")

    str_location_rule = eval(location_rule, json_data)
    # 当演员为空时，location_rule被计算为'/number'绝对路径，导致路径连接忽略第一个路径参数，因此添加./使其始终为相对路径
    success_folder = config.getStrValue("common.success_output_folder")
    path = os.path.join(success_folder, f'./{str_location_rule.strip()}')
    path = escape_path(path, config.getStrValue("Name_Rule.literals"))
    
    try:
        create_folder(path)
    except:
        logger.error(f"Fatal error! Can not make folder [{path}]")
        return None

    return os.path.normpath(path)


def image_download(url:str, full_filepath:str) -> bool:
    if config.getBoolValue("common.download_only_missing_images") and not file_not_exist_or_empty(full_filepath):
        logger.info(f"image [{full_filepath}] already exists. skip download.")
        return True
    
    download(url, full_filepath)

    if not file_not_exist_or_empty(full_filepath):
        logger.info(f"download image [{full_filepath}] success.")
        return True
    else:
        logger.error("download image error.")
        return False


# 剧照下载成功，否则移动到failed
def extrafanart_download(data, movie_path):
    extrafanart_path = os.path.join(movie_path, config.getStrValue("extrafanart.extrafanart_folder_name"))
    if config.getIntValue("extrafanart.parallel_download") > 0:
        extrafanart_download_threadpool(data, extrafanart_path)
    else:
        create_folder(extrafanart_path)
        for index, url in enumerate(data, start=1):
            jpg_filename = f'extrafanart-{index}{image_ext(url)}'
            jpg_fullpath = os.path.join(extrafanart_path, jpg_filename)
            image_download(url,jpg_fullpath)

def extrafanart_download_threadpool(url_list, extrafanart_path):    
    dn_list = []
    for i, url in enumerate(url_list, start=1):
        jpg_fullpath = extrafanart_path / f'extrafanart-{i}{image_ext(url)}'
        if config.getBoolValue("common.download_only_missing_images") and not file_not_exist_or_empty(jpg_fullpath):
            continue
        dn_list.append((url, jpg_fullpath))

    if not len(dn_list):
        return
    
    parallel = min(len(dn_list), config.getIntValue("extrafanart.parallel_download"))

    with ThreadPoolExecutor(parallel) as pool:
        results = list(pool.map(download_one_file, dn_list))

    succ = 0
    for r in results:
        if r:
            succ += 1
    logger.info(f"download extrafanart images done. [{succ}/{len(results)}] successfully. ")

def download_one_file(args):
    (url, save_path) = args
    return image_download(url, save_path)