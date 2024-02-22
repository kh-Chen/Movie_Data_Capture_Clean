import os
import re
from .scrapinglib.base import Scraper
import logger
import config
from utils.functions import special_characters_replacement
import translators as ts

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


    

'''格式化scrapinglib的刮削结果'''
def cover_json_data(movie_info):
    actor_list = ["佚名"]
    if 'actor' in movie_info:
        actor_list = movie_info['actor']
        if not isinstance(actor_list, list):
            actor_list = [ actor_list ]
    actor_list = [actor.strip() for actor in actor_list]
    actor_list = [special_characters_replacement(a) for a in actor_list]
    actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')
    movie_info['actor_list'] = actor_list
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
    movie_info["director"] = special_characters_replacement(movie_info["director"]) if 'director' in movie_info else ''
    movie_info["release"] = movie_info["release"].replace('/', '-') if 'release' in movie_info else ''
    movie_info["studio"] = special_characters_replacement(movie_info["studio"]) if 'studio' in movie_info else ''
    movie_info["title"] = special_characters_replacement(movie_info["title"]) if 'title' in movie_info else ''
    movie_info["original_title"] = movie_info["title"]
    movie_info["title"] = movie_info["title"].replace(movie_info["actor"].replace(","," "),"").strip()
    movie_info["outline"] = special_characters_replacement(movie_info["outline"]) if 'outline' in movie_info else ''
    movie_info["label"] = special_characters_replacement(movie_info["label"]) if 'label' in movie_info else ''
    movie_info["series"] = special_characters_replacement(movie_info["series"]) if 'series' in movie_info else ''
    movie_info['trailer'] = special_characters_replacement(movie_info["trailer"]) if 'trailer' in movie_info else ''
    movie_info['extrafanart'] = special_characters_replacement(movie_info["extrafanart"]) if 'extrafanart' in movie_info else ''

    title = movie_info["title"]
    outline = movie_info["outline"]
    if config.getBoolValue("translate.switch"):
        translator = config.getStrValue("translate.engine")
        try:
            title = ts.translate_text(query_text=title, translator=translator, from_language='jp', to_language='zh', timeout=10)
        except Exception as e:
            logger.error(f"translate title error. text:{title} e:{e}")
        if outline.strip() != '':
            outline = ts.translate_text(query_text=outline, translator=translator, from_language='ja', to_language='zh-CHS', timeout=10)
    
    outline = f"{movie_info['number']} # {outline if outline.strip() != '' else title}"

    movie_info["title"] = title
    movie_info["outline"] = outline

    if 'website' in movie_info:
        movie_info["website_id"] = movie_info["website"].split("/")[-1]
    

    return movie_info





