import os
import sys 
import platform
import signal
import time
import threading

import logger
import config
from config import constant
import core.process_control as process_control
from utils.event import fire_event

def signal_handler(*args):
    logger.info("Ctrl+C detected! ")

    threading.Thread(target=fire_event, args=["SIGINT"]).start()
    def a():
        wait = max(10,config.getIntValue("common.interval")+3)
        for i in range(wait, -1, -1):
            logger.info(f"Exit in {i}...")
            time.sleep(1)
        os._exit(0)
    threading.Thread(target=a).start()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    config.init()

    enable_debug = config.getBoolValue("common.enable_debug")
    if enable_debug:
        logger.enable_debug()

    platform_total = str(' - ' + platform.platform() + ' \n[*] - ' + platform.machine() + ' - Python-' + platform.python_version())
    logger.info('================= Movie Data Capture =================')
    logger.info(f"Ver. {constant.G_VERSION}".center(51))
    logger.info('======================================================')
    logger.info(platform.platform().center(51))
    logger.info(f"{platform.machine()} - Python - {platform.python_version()}".center(51))
    logger.info(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())).center(51))
    logger.info('======================================================')
    logger.info(f"CmdLine [{' '.join(sys.argv)}]")
    logger.info('======================================================')
        # print('[!]CmdLine:', " ".join())
    # logger.info(' - 请不要在墙内宣传本项目 - ')
    

    process_control.start()
    logger.info("end.")

    