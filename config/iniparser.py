import os
import configparser
import logger

import config.variables as variables

def parse() -> bool:
    ini_path = None
    conf_file_path = variables.args["conf_file_path"]
    if conf_file_path != '':
        if not os.path.isfile(conf_file_path):
            logger.error(f"{conf_file_path} file not found!")
            return False
        else:
            ini_path = conf_file_path
    else:
        path_search_order = (
            'config.ini',
            'static/config-default.ini'
        )
        for p in path_search_order:
            if os.path.isfile(p):
                ini_path = p
                break
        if ini_path is None:
            logger.error("config.ini not found!")
            return False
    
    variables.conf["conf_file_path"] = os.path.abspath(p)
    logger.debug(f"find config.ini at {variables.conf['conf_file_path']}")
    try:
        parser = configparser.ConfigParser()
        parser.read(ini_path, encoding="utf-8")     
    except Exception as e:
        logger.error(f"parse {ini_path} error! error message:{e}")
        return False
    
    for section in parser.sections():
        for key in parser[section]:
            variables.conf[f"{section}.{key}"] = parser[section][key]

    

