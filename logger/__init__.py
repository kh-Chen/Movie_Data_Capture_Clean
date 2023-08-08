from logging import Logger
import logging.config

logging.config.fileConfig(fname='static/logger-default.ini', disable_existing_loggers=False)

my_logger = logging.getLogger()
def get_real_logger() -> Logger:
     return my_logger
     
def debug(str: str):
    my_logger.debug(str)

def info(str: str):
    my_logger.info(str)

def warning(str: str):
    my_logger.warning(str)

def error(str: str):
    my_logger.error(str)

def enable_debug():
    my_logger.setLevel(logging.DEBUG)
    for handler in my_logger.handlers:
	    handler.setLevel(logging.DEBUG)