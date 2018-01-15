# -*- coding: utf-8 -*-
import sys
import logging

from utils import log
from utils import utils
from utils.INIParser import INIParser
from weibo import crawler as weibo_crawler

log.init_logger('crawler')
logger = logging.getLogger('crawler')
sys.stderr = log.ErrOutPutToLogger("crawler")


def main():
    ini_filename = utils.get_path_with_base_file(__file__, 'data/input.ini')
    config = INIParser.read(ini_filename)
    if config['default']['crawler_type'] == 'weibo':
        weibo_crawler.start(config)
    # logger.info(ini_filename)


if __name__ == '__main__':
    main()
