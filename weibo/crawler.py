# -*- coding: utf-8 -*-


def crawler_user_post_list(url):
    pass
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
    for url in user_urls:
        crawler_user_post_list(url)


