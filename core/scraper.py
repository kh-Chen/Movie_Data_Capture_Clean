from .scrapinglib.base import Scraper
import logger
import config
import translators as ts

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


def cover_json_data(movie_info):
    actor_list = ["佚名"]
    if 'actor' in movie_info:
        actor_list = movie_info['actor']
        if not isinstance(actor_list, list):
            actor_list = [ actor_list ]
    actor_list = [actor.strip() for actor in actor_list]
    actor_list = [special_characters_replacement(a) for a in actor_list]
    actor = str(movie_info['actor_list']).strip("[ ]").replace("'", '').replace(" ", '')
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
    movie_info["outline"] = special_characters_replacement(movie_info["outline"]) if 'outline' in movie_info else ''
    movie_info["label"] = special_characters_replacement(movie_info["label"]) if 'label' in movie_info else ''
    movie_info["series"] = special_characters_replacement(movie_info["series"]) if 'series' in movie_info else ''
    movie_info['trailer'] = special_characters_replacement(movie_info["trailer"]) if 'trailer' in movie_info else ''
    movie_info['extrafanart'] = special_characters_replacement(movie_info["extrafanart"]) if 'extrafanart' in movie_info else ''

    if config.getBoolValue("translate.switch"):
        movie_info["title"] = ts.translate_text(query_text=movie_info["title"], translator='caiyun', from_language='ja', to_language='zh-CHS', timeout=10)
        movie_info["outline"] = ts.translate_text(query_text=movie_info["outline"], translator='caiyun', from_language='ja', to_language='zh-CHS', timeout=10)
    
    naming_rule = ""
    original_naming_rule = ""
    for i in config.getStrValue("Name_Rule.naming_rule").split("+"):
        if i not in movie_info:
            naming_rule += i.strip("'").strip('"')
            original_naming_rule += i.strip("'").strip('"')
        else:
            item = movie_info[i]
            naming_rule += item if type(item) is not list else "&".join(item)
            if i == 'title':
                item = movie_info.get('original_title')
            original_naming_rule += item if type(item) is not list else "&".join(item)

    movie_info['naming_rule'] = naming_rule
    movie_info['original_naming_rule'] = original_naming_rule
    return movie_info




def special_characters_replacement(text) -> str:
    if not isinstance(text, str):
        return text
    return (text.replace('\\', '∖').  # U+2216 SET MINUS @ Basic Multilingual Plane
            replace('/', '∕').  # U+2215 DIVISION SLASH @ Basic Multilingual Plane
            replace(':', '꞉').  # U+A789 MODIFIER LETTER COLON @ Latin Extended-D
            replace('*', '∗').  # U+2217 ASTERISK OPERATOR @ Basic Multilingual Plane
            replace('?', '？').  # U+FF1F FULLWIDTH QUESTION MARK @ Basic Multilingual Plane
            replace('"', '＂').  # U+FF02 FULLWIDTH QUOTATION MARK @ Basic Multilingual Plane
            replace('<', 'ᐸ').  # U+1438 CANADIAN SYLLABICS PA @ Basic Multilingual Plane
            replace('>', 'ᐳ').  # U+1433 CANADIAN SYLLABICS PO @ Basic Multilingual Plane
            replace('|', 'ǀ').  # U+01C0 LATIN LETTER DENTAL CLICK @ Basic Multilingual Plane
            replace('&lsquo;', '‘').  # U+02018 LEFT SINGLE QUOTATION MARK
            replace('&rsquo;', '’').  # U+02019 RIGHT SINGLE QUOTATION MARK
            replace('&hellip;', '…').
            replace('&amp;', '＆').
            replace("&", '＆')
            )

