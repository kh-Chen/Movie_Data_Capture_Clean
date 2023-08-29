import re,os,time
from datetime import datetime
import typing
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import shutil
from lxml import etree

import logger
import config
from config import constant
from . import mode_list_movie
from . import scraper
from utils.number_parser import get_number
from utils.functions import create_folder,image_ext,file_not_exist_or_empty,legalization_of_file_path
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
        logger.info(f"-----------running {percentage} [{processed}/{count_all}]-----------")
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
    
    movie_info = scraper.get_base_data_by_number(number)
    if movie_info is None:
        moveFailedFolder(movie_path)
        return
    
    filename = os.path.basename(movie_path)
    movie_info["cn_sub"] = "-C" if re.search(r'[-_]C(\.\w+$|-\w+)|\d+ch(\.\w+$|-\w+)', filename, re.I) \
        or '中文' in filename or '字幕' in filename else ""
    
    main_mode = config.getIntValue("common.main_mode")
    if main_mode == 1:
        main_mode_1(movie_path, movie_info)
    elif main_mode == 2:
        pass
    elif main_mode == 3:
        pass


def main_mode_1(movie_path, movie_info):
    number = movie_info["number"]

    movie_target_dir = create_movie_folder_by_rule(movie_info)
    if movie_target_dir is None:
        moveFailedFolder(movie_path)
        return
    
    # 处理封面
    fanart_path = ''
    poster_path = ''
    thumb_path = ''
    if config.getBoolValue("capture.get_cover_switch"):
        fanart_path, poster_path, thumb_path = handler_cover(movie_info, movie_target_dir)
    # 下载预告片
    # if conf.is_trailer() and movie_info.get('trailer'):
    #     trailer_download(movie_info.get('trailer'), leak_word, c_word, hack_word, number, path, movie_path)

    # 下载剧照
    if config.getBoolValue("capture.get_extrafanart_switch") and "extrafanart" in movie_info and len(movie_info.get('extrafanart')) > 0:
        extrafanart_download(movie_info.get('extrafanart'), movie_target_dir)

    # 下载演员头像 KODI .actors 目录位置
    # if conf.download_actor_photo_for_kodi():
    #     actor_photo_download(movie_info.get('actor_photo'), path, number)
    
    movie_suffix = os.path.splitext(movie_path)[-1]
    movie_file_name_template = config.getStrValue("template.movie_file_name_template")
    logger.debug(f"movie_file_name_template: [{movie_file_name_template}]")
    target_file_name = movie_file_name_template.format(**movie_info)

    # 生成nfo文件
    if config.getBoolValue("capture.write_nfo_switch"):
        nfo_path = os.path.join(movie_target_dir, f"{target_file_name}.nfo")
        try:
            print_nfo_file(nfo_path,fanart_path,poster_path,thumb_path,movie_info)
        except Exception as e:
            logger.error(f"print_files error. [{e}]")
            moveFailedFolder(movie_path)
            return
    
    # TODO link mode
    new_movie_path = legalization_of_file_path(os.path.join(movie_target_dir, target_file_name + movie_suffix))
    logger.info(f"{movie_path} move to {new_movie_path}")
    shutil.move(movie_path, new_movie_path)

    for sub_suffix in constant.G_SUB_SUFFIX:
        l = len(movie_path)-len(movie_suffix)
        sub_path = movie_path[:l]+sub_suffix
        if os.path.isfile(sub_path):
            target_sub_path = os.path.join(movie_target_dir, target_file_name + sub_suffix)
            logger.info(f"find sub file at [{sub_path}], move to [{target_sub_path}]")
            shutil.move(sub_path, target_sub_path)


def handler_cover(movie_info, movie_target_dir):
    number = movie_info["number"]
    fanart_path = ""
    poster_path = ""
    thumb_path = ""
    if "cover" in movie_info and movie_info["cover"] != '':
        cover_url = movie_info["cover"]
        ext = image_ext(cover_url)
        fanart_path = f"fanart{ext}"
        poster_path = f"poster{ext}"
        thumb_path = f"thumb{ext}"
        if config.getBoolValue("capture.cover_naming_with_number"):
            fanart_path = f"{number}{movie_info['cn_sub']}-fanart{ext}"
            poster_path = f"{number}{movie_info['cn_sub']}-poster{ext}"
            thumb_path = f"{number}{movie_info['cn_sub']}-thumb{ext}"
        
        full_filepath = os.path.join(movie_target_dir, thumb_path)
        succ = image_download(cover_url, full_filepath)
        shutil.copyfile(full_filepath, os.path.join(movie_target_dir, poster_path))
        if succ and not config.getBoolValue("common.jellyfin"):
            shutil.copyfile(full_filepath, os.path.join(movie_target_dir, fanart_path))
            # TODO cutImage(imagecut, path, thumb_path, poster_path, bool(conf.face_uncensored_only() and not uncensored))
    
    return fanart_path, poster_path, thumb_path




def moveFailedFolder(movie_path):
    failed_folder = config.getStrValue("common.failed_output_folder")
    new_movie_path = os.path.join(failed_folder, os.path.basename(movie_path))
    mtxt = os.path.abspath(os.path.join(failed_folder, 'where_was_i_before_being_moved.txt'))
    logger.info(f"Move to Failed output folder, see {mtxt}")

    with open(mtxt, 'a', encoding='utf-8') as wwibbmt:
        tmstr = datetime.now().strftime("%Y-%m-%d %H:%M")
        wwibbmt.write(f'{tmstr} FROM[{movie_path}] TO [{new_movie_path}]\n')
    try:
        if os.path.exists(new_movie_path):
            logger.error(f"File Exists while moving to FailedFolder: [{new_movie_path}]")
            return
        shutil.move(movie_path, new_movie_path)
    except Exception as e:
        logger.error(f"File Moving to FailedFolder unsuccessful! file: [{movie_path}], msg:[{e}]")


def create_movie_folder_by_rule(movie_info):
    success_folder = config.getStrValue("common.success_output_folder")
    location_template = config.getStrValue("template.location_template")
    relative_path = location_template.format(**movie_info)
    path = os.path.join(success_folder, f'./{relative_path.strip()}')
    path = legalization_of_file_path(path)
    
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


def extrafanart_download(data, movie_target_dir):
    extrafanart_path = os.path.join(movie_target_dir, config.getStrValue("capture.extrafanart_folder_name"))
    create_folder(extrafanart_path)
    if config.getIntValue("capture.extrafanart_parallel_download") > 0:
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
        jpg_fullpath = os.path.join(extrafanart_path, f'extrafanart-{i}{image_ext(url)}') 
        if config.getBoolValue("common.download_only_missing_images") and not file_not_exist_or_empty(jpg_fullpath):
            continue
        dn_list.append((url, jpg_fullpath))

    if not len(dn_list):
        return
    
    parallel = min(len(dn_list), config.getIntValue("capture.extrafanart_parallel_download"))

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



def print_nfo_file(nfo_path, fanart_path, poster_path, thumb_path, movie_info):
    jellyfin = config.getBoolValue("common.jellyfin")
    try:
        old_nfo = None
        try:
            if os.path.isfile(nfo_path):
                old_nfo = etree.parse(nfo_path)
        except:
            pass

        nfo_title = ""
        original_nfo_title = ""
        nfo_title_template = config.getStrValue("template.nfo_title_template")
        nfo_title = nfo_title_template.format(**movie_info)
        original_nfo_title = nfo_title_template.replace('{title}', '{original_title}').format(**movie_info)

        with open(nfo_path, "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
            print("<movie>", file=code)
            if not jellyfin:
                print("  <title><![CDATA[" + nfo_title + "]]></title>", file=code)
                print("  <originaltitle><![CDATA[" + original_nfo_title + "]]></originaltitle>",
                      file=code)
                print("  <sorttitle><![CDATA[" + nfo_title + "]]></sorttitle>", file=code)
            else:
                print("  <title>" + nfo_title + "</title>", file=code)
                print("  <originaltitle>" + original_nfo_title + "</originaltitle>", file=code)
                print("  <sorttitle>" + nfo_title + "</sorttitle>", file=code)
            print("  <customrating>JP-18+</customrating>", file=code)
            print("  <mpaa>JP-18+</mpaa>", file=code)
            try:
                print("  <set>" + movie_info['series'] + "</set>", file=code)
            except:
                print("  <set></set>", file=code)
            print("  <studio>" + movie_info['studio'] + "</studio>", file=code)
            print("  <year>" + movie_info['year'] + "</year>", file=code)
            if not jellyfin:
                print("  <outline><![CDATA[" + movie_info['outline'] + "]]></outline>", file=code)
                print("  <plot><![CDATA[" + movie_info['outline'] + "]]></plot>", file=code)
            else:
                print("  <outline>" + movie_info['outline'] + "</outline>", file=code)
                print("  <plot>" + movie_info['outline'] + "</plot>", file=code)
            print("  <runtime>" + str(movie_info['runtime']).replace(" ", "") + "</runtime>", file=code)
            print("  <director>" + movie_info['director'] + "</director>", file=code)
            print("  <poster>" + poster_path + "</poster>", file=code)
            print("  <thumb>" + thumb_path + "</thumb>", file=code)
            if not jellyfin:  # jellyfin 不需要保存fanart
                print("  <fanart>" + fanart_path + "</fanart>", file=code)
            try:
                for key in movie_info['actor_list']:
                    print("  <actor>", file=code)
                    print("    <name>" + key + "</name>", file=code)
                    # try:
                    #     print("    <thumb>" + actor_photo.get(str(key)) + "</thumb>", file=code)
                    # except:
                    #     pass
                    print("  </actor>", file=code)
            except:
                pass
            print("  <maker>" + movie_info['studio'] + "</maker>", file=code)
            print("  <label>" + movie_info['label'] + "</label>", file=code)

            
            if not jellyfin:
                for i in movie_info['tag']:
                    print("  <tag>" + i + "</tag>", file=code)
            else:
                for i in movie_info['tag']:
                    print("  <genre>" + i + "</genre>", file=code)

            print("  <num>" + movie_info['number'] + "</num>", file=code)
            print("  <premiered>" + movie_info['release'] + "</premiered>", file=code)
            print("  <releasedate>" + movie_info['release'] + "</releasedate>", file=code)
            print("  <release>" + movie_info['release'] + "</release>", file=code)
            if old_nfo:
                try:
                    xur = old_nfo.xpath('//userrating/text()')[0]
                    if isinstance(xur, str) and re.match('\d+\.\d+|\d+', xur.strip()):
                        print(f"  <userrating>{xur.strip()}</userrating>", file=code)
                except:
                    pass
            try:
                f_rating = movie_info.get('userrating')
                uc = movie_info.get('uservotes')
                print(f"""  <rating>{round(f_rating * 2.0, 1)}</rating>
  <criticrating>{round(f_rating * 20.0, 1)}</criticrating>
  <ratings>
    <rating name="javdb" max="5" default="true">
      <value>{f_rating}</value>
      <votes>{uc}</votes>
    </rating>
  </ratings>""", file=code)
            except:
                if old_nfo:
                    try:
                        for rtag in ('rating', 'criticrating'):
                            xur = old_nfo.xpath(f'//{rtag}/text()')[0]
                            if isinstance(xur, str) and re.match('\d+\.\d+|\d+', xur.strip()):
                                print(f"  <{rtag}>{xur.strip()}</{rtag}>", file=code)
                        f_rating = old_nfo.xpath(f"//ratings/rating[@name='javdb']/value/text()")[0]
                        uc = old_nfo.xpath(f"//ratings/rating[@name='javdb']/votes/text()")[0]
                        print(f"""  <ratings>
    <rating name="javdb" max="5" default="true">
      <value>{f_rating}</value>
      <votes>{uc}</votes>
    </rating>
  </ratings>""", file=code)
                    except:
                        pass
            print("  <cover>" + movie_info['cover'] + "</cover>", file=code)
            # if config.getInstance().is_trailer():
            #     print("  <trailer>" + trailer + "</trailer>", file=code)
            print("  <website>" + movie_info['website'] + "</website>", file=code)
            print("</movie>", file=code)
            logger.info(f"nfo file wrote! [{nfo_path}]")    
    except Exception as e:
        logger.error(f"nfo file write error! [{nfo_path}] {e}")
        return
