import re,os
import typing
from pathlib import Path

import logger
import config
from config import constant
from utils.number_parser import get_number
from utils.functions import file_modification_days

def run():
    list = movie_lists()
    logger.info("get movie list: ")
    for str in list:
        try: 
            number = get_number(str)
            print(f"{number:{10}}|{str}")
        except Exception as e:
            logger.error(f"getnumber error. file: {str} {e}")
        

def movie_lists() -> typing.List[str]:

    source_folder = config.getStrValue("common.source_folder")
    if not isinstance(source_folder, str) or source_folder == '':
        source_folder = os.path.abspath(".")

    logger.info(f"scan movie at {source_folder}")

    # main_mode = config.getIntValue("common.main_mode")
    nfo_skip_days = config.getIntValue("common.nfo_skip_days")
    escape_folder_set = set(re.split("[,，]", config.getStrValue("common.escape_folders")))
    
    total = []
    source = Path(source_folder).resolve()
    
    for full_name in source.glob(r'**/*'):
        if set(full_name.parent.parts) & escape_folder_set:
            continue
        if not full_name.is_file():
            continue
        if not full_name.suffix.lower() in constant.G_MEDIA_SUFFIX:
            continue
        
        # if re.compile(r'-trailer\.', re.IGNORECASE).search(full_name.name):#预告片
        #     continue

        # 调试用0字节样本允许通过，去除小于120MB的广告
        movie_size = 0 if full_name.is_symlink() else full_name.stat().st_size  # 符号链接不取stat()及st_size
        if 0 < movie_size < 125829120:  # 1024*1024*120=125829120
            continue

        nfo = full_name.with_suffix('.nfo')
        if nfo_skip_days > 0 and nfo.is_file() and file_modification_days(nfo) <= nfo_skip_days:
            skip_nfo_days_cnt += 1
            continue

        total.append(str(full_name))

    return total