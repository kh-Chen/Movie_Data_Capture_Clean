import sys 
import platform

import logger
import config
import core.process_control as process_control

if __name__ == '__main__':
    config.init()

    enable_debug = config.getBoolValue("common.enable_debug")
    if enable_debug:
        logger.enable_debug()

    platform_total = str(' - ' + platform.platform() + ' \n[*] - ' + platform.machine() + ' - Python-' + platform.python_version())
    logger.info('================= Movie Data Capture =================')
    logger.info(f"Ver. {config.G_VERSION}".center(51))
    logger.info('======================================================')
    logger.info(platform.platform())
    logger.info(f"{platform.machine()} - Python - {platform.python_version()}")
    logger.info('======================================================')
    logger.info(f"CmdLine [{' '.join(sys.argv)}]")
    logger.info('======================================================')
        # print('[!]CmdLine:', " ".join())
    # logger.info(' - 请不要在墙内宣传本项目 - ')
    

    process_control.start()
    logger.info("end.")

    