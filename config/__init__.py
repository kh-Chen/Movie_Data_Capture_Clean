import logger
import config.argsparser as argsparser
import config.iniparser as iniparser
import config.variables as variables

G_VERSION = variables.G_VERSION

def init():
    argsparser.parse()
    iniparser.parse()

def getStrValAtConf(key:str = "") -> str:
    return variables.conf[key] if key in variables.conf else ""

def getStrValAtArgs(key:str = "") -> str:
    return variables.args[key] if key in variables.args else ""

def getStrValue(key:str = "") -> str:
    return getStrValAtConf(key) if getStrValAtArgs(key) == "" else getStrValAtArgs(key)

def getIntValue(key:str = "") -> int:
    value = getStrValue(key)
    try:
        return int(value)
    except:
        logger.error(f"config.getIntValue error! cannot parse to int. value: {value} ")
        return None

def getBoolValue(key:str = "") -> int:
    return bool(getIntValue(key))