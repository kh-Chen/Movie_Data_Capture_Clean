import logger
import config.argsparser as argsparser
import config.iniparser as iniparser
import config.variables as variables

def init():
    argsparser.parse()
    iniparser.parse()

def getStrValAtConf(key:str = "") -> str:
    return str(variables.conf[key]) if key in variables.conf else ""

def getStrValAtArgs(key:str = "") -> str:
    return str(variables.args[key]) if key in variables.args else ""

def getOriginalValAtArgs(key:str = "") :
    return variables.args[key] if key in variables.args else None

def getBoolValAtArgs(key:str = "", default:bool=False) -> bool:
    if not key in variables.args:
        return default
    
    value = variables.args[key]
    if isinstance(value, bool):
        return value
    
    try:
        return bool(value)
    except Exception as e:
        logger.error(f"config.getBoolValAtArgs error! cannot parse to bool. key: [{key}] value: {value} ")
        return default


def getStrValue(key:str = "") -> str:
    return getStrValAtConf(key) if getOriginalValAtArgs(key) is None else getStrValAtArgs(key)

def getIntValue(key:str = "") -> int:
    value = getStrValue(key)
    try:
        return int(value)
    except:
        logger.error(f"config.getIntValue error! cannot parse to int. key: [{key}] value: {value} ")
        return None

def getBoolValue(key:str = "") -> int:
    return bool(getIntValue(key))

def setStrValAtConf(key:str, val:str) -> str:
    variables.conf[key] = val