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
    return int(getStrValue(key))

def getBoolValue(key:str = "") -> int:
    return bool(getStrValue(key))