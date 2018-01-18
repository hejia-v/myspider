# -*- coding: utf-8 -*-
import logging
import json
import time
import random
import requests
import urllib.parse

from utils import utils
from utils import nodejs
from weibo import mdata

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
    return text


def wait(interval=None):
    if interval is None:
        interval = 2 + random.random() * (6 - 2)
    logger.info(f'wait: {interval}')
    time.sleep(interval)


def read_cookies():
    cookies_file = utils.get_path_with_base_file(__file__, '../data/weibo.cookies')
    with open(cookies_file, 'rt', encoding='utf-8') as fd:
        cookies_lines = [l.strip() for l in fd.readlines() if l.strip()]
    cookies_lines = [l.partition(':') for l in cookies_lines]
    cookies_lines = [(l[0].strip(), l[2].strip()) for l in cookies_lines]
    cookies = dict(cookies_lines)
    return cookies


g_cookie = {}


def get(url):
    global g_cookie
    headers = {'user-agent': USER_AGENT}
    r = session.get(url, headers=headers)
    return r


def login():
    r = get(FAVHOME)
    # r.encoding = 'gbk'
    text = r.text
    # debug_record(text)

    result = nodejs.run_nodejs(SCRIPT_PATH, ['1'], text)
    json_obj = json.loads(result, encoding='utf-8')
    logger.info(json_obj)
    logger.info(f"微博昵称: {json_obj['nick']}")
    logger.info('登录成功')


def crawler_user_post_list(uid):
    logger.info(uid)
    home_url = f'https://m.weibo.cn/u/{uid}'
    logger.info(f'home: {home_url}')
    headers = {'user-agent': USER_AGENT}
    r = session.get(home_url, headers=headers)
    logger.info(f'get: {home_url}')

    params = r.cookies['M_WEIBOCN_PARAMS']
    params = urllib.parse.unquote(params)
    params = urllib.parse.parse_qsl(params)
    params = dict(params)
    fid = params['fid']
    logger.info(f'fid: {fid}')

    wait(1)

    url = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}&containerid={fid}'
    r = session.get(url, headers=headers)
    logger.info(f'get: {url}')
    data = r.json()
    containerid = data['data']['tabsInfo']['tabs'][1]['containerid']

    wait(1)

    page = 0
    while True:
        page += 1
        url = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={uid}&containerid={containerid}&page=1'
        r = session.get(url, headers=headers)
        logger.info(f'get: {url}')
        data = r.json()
        cards = data['data']['cards']
        print(cards)
        debug_record(str(cards))
        bsucc = mdata.add_card_list_data(cards)
        if not bsucc:
            break
        break
        wait()
    # debug_record(str(r.cookies.get_dict()))
    # debug_record(str(data))



    # r = get(url)
    # r.encoding = 'utf-8'
    # text = r.text
    # debug_record(text)
    # text = text.encode('gbk').decode('utf-8')

    # post can't change
    # 持久化 __repr__ serilizon load ----
    # requst url  un persiset
    # text resp
    # parser post list
    # post_obj list  first fill base info
    # 持久化 __repr__ serilizon





def start(config):
    uid_list = []
    if config['weibo.crawler']['crawler_all']:
        uid_list = config['weibo.uid']
    else:
        index = config['weibo.crawler']['crawler_user_index']
        if 0 <= index < len(config['weibo.uid']):
            uid_list.append(config['weibo.uid'][index])

    # login()
    # time.sleep(1.5)
    for uid in uid_list:
        crawler_user_post_list(uid)
