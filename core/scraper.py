import os
import re
from .scrapinglib.base import Scraper
import logger
import config
from utils.functions import special_characters_replacement
from utils import translate

'''
刮削器转接层。将外围业务逻辑与核心刮削器scrapinglib解耦
'''
def get_base_data_by_number(number:str):
    logger.debug(f"get Data for number [{number}]...")
    sc = Scraper()
    json_data = sc.search(number)
    if not json_data:
        logger.error(f'Movie Number [{number}] not found!')
        return None
    if str(json_data.get('number')).upper() != number.upper():
        logger.error(f'Movie Number [{number}] mismatch to [{json_data.get("number")}]!')
        return None
    if json_data.get('title') == '':
        logger.error('Movie Title not found!')
        return None

    return cover_json_data(json_data)


'''
在文件名中查找信息并补充进movie_info对象
传入文件名或文件路径
'''
def get_data_at_file_name(movie_path:str, number:str):
    filename = os.path.basename(movie_path).lower()
    number = number.lower()
    movie_info = {}
    movie_info["hacked_cn_suffix"] = ''
    
    has_cn = number+"-uc" in filename or number+"-c" in filename or '中文' in filename or '字幕' in filename
    hacked = number+"-uc" in filename or '破解' in filename or '无码' in filename

    if has_cn and hacked:
        movie_info["hacked_cn_suffix"] = "-UC"
    elif has_cn:
        movie_info["hacked_cn_suffix"] = "-C"
    elif hacked:
        movie_info["hacked_cn_suffix"] = "-U"
    

    movie_info["part_num"] = 0
    movie_info["part_sub"] = ''
    result = re.search(r'(-|_)(cd)(\d+)', filename)
    if result is not None :
        movie_info["part_num"] = result.group(3)
        movie_info["part_sub"] = f'-CD{movie_info["part_num"]}'
    return movie_info
    

'''格式化scrapinglib的刮削结果'''
def cover_json_data(movie_info):
    actor_list = ["佚名"]
    if 'actor' in movie_info:
        actor_list = movie_info['actor']
        if not isinstance(actor_list, list):
            actor_list = [ actor_list ]
    actor_list = [actor.strip() for actor in actor_list]
    actor_list = [special_characters_replacement(a) for a in actor_list]
    movie_info['actor_list'] = actor_list

    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')
    movie_info['actor'] = special_characters_replacement(actor)

    tag_list = []
    if 'tag' in movie_info:
        tag_list = movie_info['tag']
        if not isinstance(tag_list, list):
            actor_list = [ tag_list ]
    while 'XXXX' in tag_list:
        tag_list.remove('XXXX')
    while 'xxx' in tag_list:
        tag_list.remove('xxx')
    movie_info['tag'] = [special_characters_replacement(t) for t in tag_list]


    movie_info["number"] = movie_info["number"].upper()
    movie_info["release"] = movie_info["release"].replace('/', '-') if 'release' in movie_info else ''
    movie_info["original_title"] = special_characters_replacement(movie_info["title"]) if 'title' in movie_info else ''
    movie_info["title"] = movie_info["title"].replace(movie_info["actor"].replace(","," "),"").strip()
    
    if config.getBoolValue("translate.switch"):
        try:
            keys = config.getStrValue("translate.values").split(',')
            for key in keys:
                if movie_info[key] is None or movie_info[key] == '':
                    continue
                value = translate.translate_text(movie_info[key])
                movie_info[key] = special_characters_replacement(value)
        except Exception as e:
            logger.error(f"translate title error. e:{e}")
        
    outline = movie_info["outline"]
    movie_info["outline"] = f"{movie_info['number']} # {outline if outline.strip() != '' else movie_info['title']}"
    
    movie_info["studio"] = special_characters_replacement(movie_info["studio"]) if 'studio' in movie_info else ''
    movie_info["label"] = special_characters_replacement(movie_info["label"]) if 'label' in movie_info else ''
    movie_info["series"] = special_characters_replacement(movie_info["series"]) if 'series' in movie_info else ''
    movie_info['trailer'] = special_characters_replacement(movie_info["trailer"]) if 'trailer' in movie_info else ''
    movie_info["director"] = special_characters_replacement(movie_info["director"]) if 'director' in movie_info else ''

    # movie_info['extrafanart'] = special_characters_replacement(movie_info["extrafanart"]) if 'extrafanart' in movie_info else ''

    if 'website' in movie_info:
        movie_info["website_id"] = movie_info["website"].split("/")[-1]
    

    return movie_info





