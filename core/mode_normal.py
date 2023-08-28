import re,os,time
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
    
    cn_sub = False
    if re.search(r'[-_]C(\.\w+$|-\w+)|\d+ch(\.\w+$|-\w+)', movie_path,
                 re.I) or '中文' in movie_path or '字幕' in movie_path:
        cn_sub = True
    
    # 处理封面
    fanart_path = ""
    poster_path = ""
    thumb_path = ""
    if "cover" in movie_info and movie_info["cover"] != '':
        cover_url = movie_info["cover"]
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
        # if conf.is_trailer() and movie_info.get('trailer'):
        #     trailer_download(movie_info.get('trailer'), leak_word, c_word, hack_word, number, path, movie_path)

    # 下载剧照
    if config.getBoolValue("extrafanart.switch") and "extrafanart" in movie_info and len(movie_info.get('extrafanart')) > 0:
        extrafanart_download(movie_info.get('extrafanart'), movie_target_dir)
                

    # 下载演员头像 KODI .actors 目录位置
    # if conf.download_actor_photo_for_kodi():
    #     actor_photo_download(movie_info.get('actor_photo'), path, number)
    
    
    movie_suffix = os.path.splitext(movie_path)[-1]
    target_file_name = f"{number}{'-C' if cn_sub else ''}"

    try:
        print_nfo_file(movie_target_dir,target_file_name,fanart_path,poster_path,thumb_path,movie_info)
    except Exception as e:
        logger.error(f"print_files error. [{e}]")
        moveFailedFolder(movie_path)
        return
    
    # TODO link mode
    shutil.move(movie_path, os.path.join(movie_target_dir, target_file_name + movie_suffix))

    for sub_suffix in constant.G_SUB_SUFFIX:
        l = len(movie_path)-len(movie_suffix)
        sub_path = movie_path[:l]+sub_suffix
        if os.path.isfile(sub_path):
            target_sub_path = os.path.join(movie_target_dir, target_file_name + sub_suffix)
            logger.info(f"find sub file at [{sub_path}], move to [{target_sub_path}]")
            shutil.move(sub_path, target_sub_path)
    
    



def moveFailedFolder(movie_path):
    pass


def create_movie_folder_by_rule(movie_info):
    location_rule = config.getStrValue("Name_Rule.location_rule")
    actor = movie_info.get('actor')
    if 'actor' in location_rule and len(actor) > 100:
        location_rule = location_rule.replace("actor", "'多人作品'")

    maxlen = config.getStrValue("Name_Rule.max_title_len")
    if 'title' in location_rule and len(movie_info["title"]) > maxlen:
        shorttitle = movie_info["title"][0:maxlen]
        location_rule = location_rule.replace("title", f"'{shorttitle}'")

    str_location_rule = eval(location_rule, movie_info)
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
def extrafanart_download(data, movie_target_dir):
    extrafanart_path = os.path.join(movie_target_dir, config.getStrValue("extrafanart.extrafanart_folder_name"))
    create_folder(extrafanart_path)
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
        jpg_fullpath = os.path.join(extrafanart_path, f'extrafanart-{i}{image_ext(url)}') 
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



def print_nfo_file(movie_target_dir, target_file_name, fanart_path, poster_path, thumb_path, movie_info):
    jellyfin = config.getBoolValue("common.jellyfin")
    nfo_path = os.path.join(movie_target_dir, f"{target_file_name}.nfo")
        
    try:
        old_nfo = None
        try:
            if os.path.isfile(nfo_path):
                old_nfo = etree.parse(nfo_path)
        except:
            pass
        # KODI内查看影片信息时找不到number，配置naming_rule=number+'#'+title虽可解决
        # 但使得标题太长，放入时常为空的outline内会更适合，软件给outline留出的显示版面也较大
        outline = movie_info['outline']
        if not outline:
            pass
        elif movie_info['source'] == 'pissplay':
            outline = f"{outline}"
        else:
            outline = f"{movie_info['number']}#{outline}"

        with open(nfo_path, "wt", encoding='UTF-8') as code:
            print('<?xml version="1.0" encoding="UTF-8" ?>', file=code)
            print("<movie>", file=code)
            if not jellyfin:
                print("  <title><![CDATA[" + movie_info['naming_rule'] + "]]></title>", file=code)
                print("  <originaltitle><![CDATA[" + movie_info['original_naming_rule'] + "]]></originaltitle>",
                      file=code)
                print("  <sorttitle><![CDATA[" + movie_info['naming_rule'] + "]]></sorttitle>", file=code)
            else:
                print("  <title>" + movie_info['naming_rule'] + "</title>", file=code)
                print("  <originaltitle>" + movie_info['original_naming_rule'] + "</originaltitle>", file=code)
                print("  <sorttitle>" + movie_info['naming_rule'] + "</sorttitle>", file=code)
            print("  <customrating>JP-18+</customrating>", file=code)
            print("  <mpaa>JP-18+</mpaa>", file=code)
            try:
                print("  <set>" + movie_info['series'] + "</set>", file=code)
            except:
                print("  <set></set>", file=code)
            print("  <studio>" + movie_info['studio'] + "</studio>", file=code)
            print("  <year>" + movie_info['year'] + "</year>", file=code)
            if not jellyfin:
                print("  <outline><![CDATA[" + outline + "]]></outline>", file=code)
                print("  <plot><![CDATA[" + outline + "]]></plot>", file=code)
            else:
                print("  <outline>" + outline + "</outline>", file=code)
                print("  <plot>" + outline + "</plot>", file=code)
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
