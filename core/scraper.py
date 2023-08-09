from .scrapinglib.base import Scraper
import logger
import config

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
    
    title = json_data.get('title')
    actor_list = str(json_data.get('actor')).strip("[ ]").replace("'", '').split(',')  # 字符串转列表
    actor_list = [actor.strip() for actor in actor_list]  # 去除空白
    director = json_data.get('director')
    release = json_data.get('release')
    number = json_data.get('number')
    studio = json_data.get('studio')
    source = json_data.get('source')
    runtime = json_data.get('runtime')
    outline = json_data.get('outline')
    label = json_data.get('label')
    series = json_data.get('series')
    year = json_data.get('year')

    cover_small = json_data.get('cover_small')  if 'cover_small' in json_data else ''
    trailer = json_data.get('trailer')  if 'trailer' in json_data else ''
    extrafanart = json_data.get('extrafanart')  if 'extrafanart' in json_data else ''

    imagecut = json_data.get('imagecut')
    tag = str(json_data.get('tag')).strip("[ ]").replace("'", '').replace(" ", '').split(',')  # 字符串转列表 @
    while 'XXXX' in tag:
        tag.remove('XXXX')
    while 'xxx' in tag:
        tag.remove('xxx')
    if json_data['source'] =='pissplay': # pissplay actor为英文名，不用去除空格
        actor = str(actor_list).strip("[ ]").replace("'", '')
    else:
        actor = str(actor_list).strip("[ ]").replace("'", '').replace(" ", '')

    # ====================处理异常字符====================== #\/:*?"<>|
    actor = special_characters_replacement(actor)
    actor_list = [special_characters_replacement(a) for a in actor_list]
    title = special_characters_replacement(title)
    label = special_characters_replacement(label)
    outline = special_characters_replacement(outline)
    series = special_characters_replacement(series)
    studio = special_characters_replacement(studio)
    director = special_characters_replacement(director)
    tag = [special_characters_replacement(t) for t in tag]
    release = release.replace('/', '-')
    tmpArr = cover_small.split(',')
    if len(tmpArr) > 0:
        cover_small = tmpArr[0].strip('\"').strip('\'')
    # ====================处理异常字符 END================== #\/:*?"<>|

    json_data['number'] = number.upper()
    json_data['title'] = title
    json_data['original_title'] = title
    json_data['actor'] = actor
    json_data['release'] = release
    json_data['cover_small'] = cover_small
    json_data['tag'] = tag
    json_data['year'] = year
    json_data['actor_list'] = actor_list
    json_data['trailer'] = trailer
    json_data['extrafanart'] = extrafanart
    json_data['label'] = label
    json_data['outline'] = outline
    json_data['series'] = series
    json_data['studio'] = studio
    json_data['director'] = director

    # TODO 翻译，简繁转换

    naming_rule = ""
    original_naming_rule = ""
    for i in config.getStrValue("Name_Rule.naming_rule").split("+"):
        if i not in json_data:
            naming_rule += i.strip("'").strip('"')
            original_naming_rule += i.strip("'").strip('"')
        else:
            item = json_data.get(i)
            naming_rule += item if type(item) is not list else "&".join(item)
            # PATCH：处理[title]存在翻译的情况，后续NFO文件的original_name只会直接沿用naming_rule,这导致original_name非原始名
            # 理应在翻译处处理 naming_rule和original_naming_rule
            if i == 'title':
                item = json_data.get('original_title')
            original_naming_rule += item if type(item) is not list else "&".join(item)

    json_data['naming_rule'] = naming_rule
    json_data['original_naming_rule'] = original_naming_rule
    return json_data



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