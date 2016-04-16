# -*- coding:utf-8 -*-
import logging


def get_logger():
    """ 配置 logger """
    logger = logging.getLogger('WeChatLog')
    logger.setLevel(logging.DEBUG)
    log_filename = "wechat_log"
    log_filename += '.log'
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(ch)

    return logger

Log = get_logger()