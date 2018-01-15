# -*- coding: utf-8 -*-
import logging
import json
import requests

from utils import utils
from utils import nodejs

logger = logging.getLogger('crawler')

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
FAVHOME = 'http://weibo.com/fav?leftnav=1'
SCRIPT_PATH = utils.get_path_with_base_file(__file__, 'parser.mjs')

session = requests.session()


def debug_record(text):
    with open('debug.html', 'wt', encoding='utf-8') as fd:
        fd.write(text)


def debug_test():
    with open('debug.html', 'rt', encoding='utf-8') as fd:
        text = fd.read()


def login():
    cookies_file = utils.get_path_with_base_file(__file__, '../data/weibo.cookies')
    with open(cookies_file, 'rt', encoding='utf-8') as fd:
        cookies_lines = [l.strip() for l in fd.readlines() if l.strip()]
    cookies_lines = [l.partition(':') for l in cookies_lines]
    cookies_lines = [(l[0].strip(), l[2].strip()) for l in cookies_lines]
    cookies = dict(cookies_lines)

    headers = {'user-agent': USER_AGENT}
    r = session.get(FAVHOME, headers=headers, cookies=cookies)
    # r.encoding = 'gbk'
    text = r.text
    debug_record(text)
    logger.info(r.cookies)

    result = nodejs.run_nodejs(SCRIPT_PATH, ['1'], text)
    json_obj = json.loads(result, encoding='utf-8')
    logger.info(json_obj)
    logger.info(f"微博昵称: {json_obj['nick']}")
    logger.info('登录成功')


def crawler_user_post_list(url):
    headers = {'user-agent': USER_AGENT}
    r = requests.get(url, headers=headers)
    r.encoding = 'gbk'
    text = r.text
    # text = text.encode('gbk').decode('utf-8')

    # post can't change
    # 持久化 __repr__ serilizon load ----
    # requst url  un persiset
    # text resp
    # parser post list
    # post_obj list  first fill base info
    # 持久化 __repr__ serilizon






def start(config):
    user_urls = []
    if config['weibo.crawler']['crawler_all']:
        user_urls = config['weibo.users']
    else:
        index = config['weibo.crawler']['crawler_user_index']
        if 0 <= index < len(config['weibo.users']):
            user_urls.append(config['weibo.users'][index])

    login()

    # for url in user_urls:
    #     crawler_user_post_list(url)
