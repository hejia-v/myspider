# -*- coding: utf-8 -*-
import sys
import logging
import os

# import weib
from utils import log
from utils.INIParser import INIParser

log.init_logger('crawler')
logger = logging.getLogger('crawler')
sys.stderr = log.ErrOutPutToLogger("crawler")


def main():
    cur_dirname = os.path.dirname(os.path.abspath(__file__))
    ini_filename = os.path.join(cur_dirname, 'data/input.ini')
    ini_filename = os.path.normpath(ini_filename)
    config = INIParser.read(ini_filename)
    pass
    print(ini_filename)
    # logger.info(ini_filename)


if __name__ == '__main__':
    main()
