from pathlib import Path
import time
import shutil
import os
import re
import json
from utils.number_parser import get_number
from core.scrapinglib.custom.javbus import Javbus
from core.scrapinglib.custom.javdb import Javdb
import logger
import config
from config import constant
from utils.functions import legalization_of_file_path
import translators as ts
from multiprocessing.dummy import Pool as ThreadPool



def main(folder_path):
    logger.info('======================= start ========================')
    movie_list = movie_lists(folder_path)
    count_all = str(len(movie_list))
    logger.info(f'Find {count_all} movies.')
    logger.info('======================================================')
    count = 0
    for movie_path in movie_list: 
        count = count + 1
        logger.info(str(count / int(count_all) * 100)[:4] + '%' + ' [' + str(count) + '/' + count_all + ']')
        create_data_and_move(movie_path, folder_path)
        time.sleep(1)
        break


def movie_lists(source_folder):
    total = []
    source = Path(source_folder).resolve()
    for full_name in source.glob(r'*'):
        if not full_name.is_file():
            continue
        if not full_name.suffix.lower() in constant.G_MEDIA_SUFFIX:
            continue

        if os.path.isfile(full_name):
            absf = str(full_name)
            total.append(absf)
    return total


def create_data_and_move(file_path: str, folder_path: str):
    n_number = get_number(os.path.basename(file_path))
    file_path = os.path.abspath(file_path)

    logger.info(f"[{n_number}] -> '{file_path}'")
    if n_number:
        try:
            core_main(file_path, folder_path, n_number)
        except Exception as e:
            logger.error(f"error. {e}")
        # cnumber = n_number+"-C"
        # if file_path.find(cnumber) == -1:
        #     suffix = os.path.splitext(file_path)[-1]
        #     findsub = False
        #     for sub_suffix in constant.G_SUB_SUFFIX:
        #         if os.path.isfile(file_path.replace(suffix,sub_suffix)):
        #             findsub = True
        #             break
        #     if findsub:
        #         return
        #     name = os.path.basename(file_path)
        #     name = name.replace(n_number, cnumber)
        #     max = 255-len(suffix)
        #     len_name = 0
        #     for index, every_char in enumerate(name):
        #         len_name += len(every_char.encode())
        #         if max < len_name:
        #             name = name[:index]+suffix
        #             break

        #     os.rename(file_path, os.path.join(folder_path,name))
    else:
        logger.info("number empty ERROR")
    logger.info("======================================================")


def core_main(file_path, folder_path, number):
    # print("[" in file_path)
    # print("]" in file_path)
    # print(os.path.basename(file_path))
    # if "[" in file_path and "]" in file_path and "／" in os.path.basename(file_path):
    #     logger.info(f"skip...")
    #     return
    
    
    # print(json_data)
    
    # path = f'{folder_path}\\{actorstr}'
    # if not os.path.exists(path):
    #     os.makedirs(path)

    suffix = os.path.splitext(file_path)[-1]
    c = file_path.lower().find(number.lower()+"-c") != -1
    # print(file_path.lower().find(number+"-c"))
    # if c :
    #     return
    # c = True
    # findsub = False
    # for sub_suffix in constant.G_SUB_SUFFIX:
    #     if os.path.isfile(file_path.replace(suffix,sub_suffix)):
    #         findsub = True
    #         break
    # if findsub:
    #     c = False

    json_data = get_data_from_json(number)
    time.sleep(1)
        

    json_data["sub"] = '-C' if c else ''
    json_data["title"] = json_data["title"].replace(json_data["actor"].replace(","," "),"").strip()
    
    name = name_template.format(**json_data)
    target = os.path.join(folder_path, f'{name}{suffix}')
    target = legalization_of_file_path(target)
    
    if os.path.basename(file_path) != os.path.basename(target):
        logger.info(f"rename to {target}")
        os.rename(file_path, target)
    else:
        logger.info(f"same name.")
    # shutil.move(filepath, f'{folder_path}\\{name}')


def get_data_from_json(file_number):  # 从JSON返回元数据
    number = file_number.upper()

    # parser = Javbus()
    parser = Javdb()

    data = parser.search(number)    
    json_data = json.loads(data)

    if len(json_data['actor']) == 0:
        json_data['actor'] = ["佚名"]
    
    json_data['actor'] = ','.join(json_data['actor'])
    return json_data


def get_data_state(data: dict) -> bool:  # 元数据获取失败检测
    if "title" not in data or "number" not in data:
        return False

    if data["title"] is None or data["title"] == "" or data["title"] == "null":
        return False

    if data["number"] is None or data["number"] == "" or data["number"] == "null":
        return False

    return True

def ttt(args):
    (translator, text) = args
    start_time = time.time()
    try:
        _from = 'auto'
        _to = 'zh-CHS'
        if translator == 'alibaba':
            _from = 'ja'
        elif translator == 'cloudTranslation':
            _to = 'zh-cn'
        elif translator == 'iflyrec':
            _from = 'ja'
        new_text = ts.translate_text(query_text=text, translator=translator, from_language=_from, to_language=_to, timeout=10)
        print(f"{new_text} ---- {translator} used time {time.time() - start_time:.3f}s")
    except Exception as e:
        # pass
        print(f"{translator} error. {e}")



name_template="{release} {number}{sub} [{userrating}/{uservotes}] {actor} {title}"
if __name__ == '__main__':
    # config.init()
    # logger.enable_debug()
    # _ = ts.preaccelerate_and_speedtest()
    translators = [
    # 'alibaba', #1
    # 'baidu', #
    # 'caiyun', #1
    # 'cloudTranslation', #
    # 'iciba', #
    'iflyrec',#3
    # 'sogou', #1
    # 'translateCom',#
    ]

    # text = "憧れの隣人の美脚お姉さんを覗き見して5日目、とうとうバレてしまうが…誘惑されてめちゃくちゃSEXした"
    # text = "死ぬほど気持ち悪い上司のデカチンに何度もイカされる屈辱レ×プ 変態上司にザーメンマーキングされた楓カレン "
    # text = "5年ぶりの夫以外との濃厚接吻に理性が飛んだ人妻のずっとベロキス中出し性交"
    text = "私のフェラ、キミの奥さんよりすっごいよ？ ～新婚の部下に追撃フェラチオ女上司～"

    mp_args = ((translator, text) for translator in translators)   
    
    with ThreadPool(len(translators)) as pool:
        results = pool.map(ttt, mp_args)
    # main('/mnt/f/store')
    # main('/mnt/f/downloaded/0')
    # main('/mnt/f/downloaded/1')
    # main('/mnt/f/downloaded/岬ななみ')
    # main('/mnt/f/downloaded/明里つむぎ')
    # main('/mnt/f/downloaded/橋本ありな')
    # main('/mnt/f/downloaded/三上悠亞')
    # main('/mnt/f/downloaded/桃乃木かな')
    # main('/mnt/f/downloaded/希島あいり')
    # main('/mnt/f/downloaded/希島あいり/1')


