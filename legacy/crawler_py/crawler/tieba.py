# -*- coding: utf-8 -*-

import re
import json
import logging
import pickle
from collections import OrderedDict
from urllib.parse import quote

import requests
from pyquery import PyQuery
from model.tieba_model import TiebaTiezi, TiebaCell, TiebaLZL

TOKEN_URL = 'https://passport.baidu.com/v2/api/?getapi&tpl=mn&apiver=v3'
INDEX_URL = 'https://www.baidu.com/'
LOGIN_URL = 'https://passport.baidu.com/v2/api/?login'
VERIFY_URL = 'http://tieba.baidu.com/f/user/json_userinfo'
CANCER_STORETHREAD_URL = 'http://tieba.baidu.com/i/submit/cancel_storethread'
OPEN_STORETHREAD_URL = 'http://tieba.baidu.com/i/submit/open_storethread'

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'

session = requests.session()
# print(dir(session))
# 添加statusCode的判断

tb_logger = logging.getLogger("crawler.tieba")


def load_cookie(filename):
    cookies = {}
    with open(filename, 'r') as f:
        text = f.read()
        for line in text.split(';'):
            line = line.strip()
            if not line:
                continue
            name, value = line.strip().split('=', 1)
            cookies[name] = value

    return cookies


def login(username, password):
    headers = {'user-agent': USER_AGENT}
    r = session.get(INDEX_URL, headers=headers)
    print('initial...')

    r = session.get(TOKEN_URL, headers=headers)
    text = r.text
    patt = re.compile("\"token\" : \"([^\"]+?)\"")
    mo = patt.search(text)
    token = mo.group(1)
    print('token: ', token)

    headers = {
        'User-Agent': USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "en-US,en;q=0.8,zh;q=0.6",
        "Host": "passport.baidu.com",
        "Origin": "http://www.baidu.com",
        "Referer": "http://www.baidu.com/",
    }

    data = {
        "staticpage": "https://passport.baidu.com/static/passpc-account/html/V3Jump.html",
        "token": token,
        "tpl": "mn",  # 重要,需要跟TOKEN_URL中的相同
        "username": username,
        "password": password,
    }
    r = session.post(LOGIN_URL, headers=headers, data=data)
    # todo: 有验证码的时候, 需要额外处理
    print('login...')

    headers = {'user-agent': USER_AGENT}
    r = session.get(VERIFY_URL, headers=headers)

    jsonObj = r.json()
    if jsonObj and jsonObj['no'] == 0:
        print('OK, login succes!')
    else:
        print('WTF, there is something wrong...')


def login_with_cookie(username, password, cookies):
    headers = {'user-agent': USER_AGENT}
    session.cookies.update(cookies)
    r = session.get(VERIFY_URL, headers=headers)

    jsonObj = r.json()
    if jsonObj and jsonObj['no'] == 0:
        print('OK, login succes!')
    else:
        print('WTF, there is something wrong...')


def get_favors(username, password):
    fstUrl = "http://tieba.baidu.com//i/sys/jump?un=%s&type=storethread" % quote(username)
    num = 1
    favthItemList = []

    def fetch_favor_page(url, num):
        print("第%d页：%s" % (num, url))
        num += 1

        headers = {'user-agent': USER_AGENT}
        r = session.get(url, headers=headers)
        text = r.text
        jq = PyQuery(text)

        def extract_favth_item(i, elem):
            j = PyQuery(elem)
            item = {
                'title': j('.favth_item_title').text().strip(),
                'forum': j('.favth_item_forum').text().strip(),
                'author': j('.favth_item_author').text().strip(),
                'status': j('.j_favth_status').text().strip(),
                'url': j('.favth_item_title a').attr('href').strip(),
            }
            favthItemList.append(item)
            # print(item)
        jq('#feed ul li').each(extract_favth_item)

        nextUrls = jq('#pager a').filter(lambda i, elem: elem.text.find('下一页') != -1)
        if len(nextUrls) >= 1:
            nextUrl = nextUrls[0].attrib['href'].strip()
            nextUrl = 'http://tieba.baidu.com' + nextUrl
            fetch_favor_page(nextUrl, num)

    fetch_favor_page(fstUrl, num)
    return favthItemList


def get_itbtbs():
    headers = {'user-agent': USER_AGENT}
    r = session.get('http://tieba.baidu.com/', headers=headers)
    text = r.text

    patt = re.compile("PageData.itbtbs = \"([^\"]+?)\"")
    mo = patt.search(text)
    itbtbs = mo.group(1)
    print('itbtbs: ', itbtbs)
    return itbtbs


def add_favors(username, password, itbtbs, favthItemList):
    for item in reversed(favthItemList):
        print(item)
        tid = item['url'][3:]
        headers = {
            'User-Agent': USER_AGENT,
            'Host': 'tieba.baidu.com',
            'Origin': 'http://tieba.baidu.com',
            'Referer': 'http://tieba.baidu.com/p/%s' % tid,
        }
        data = {
            'tbs': itbtbs,
            'tid': tid,
            'type': 0,
            'datatype': 'json',
            'ie': 'utf-8',
        }
        r = session.post(OPEN_STORETHREAD_URL, headers=headers, data=data)
        print(r.text)


def cancer_favors(username, password, itbtbs, favthItemList):
    for item in favthItemList:
        print(item)
        tid = item['url'][3:]
        headers = {
            'User-Agent': USER_AGENT,
            'Host': 'tieba.baidu.com',
            'Origin': 'http://tieba.baidu.com',
            'Referer': 'http://tieba.baidu.com/p/%s' % tid,
        }
        data = {
            'tbs': itbtbs,
            'tid': tid,
            'type': 0,
            'datatype': 'json',
            'ie': 'utf-8'
        }
        r = session.post(CANCER_STORETHREAD_URL, headers=headers, data=data)
        print(r.text)


def fetch_tiezi(url):  # 获取帖子内容
    s, _, e = url.rpartition('?pn=')
    url = s or e
    s, _, e = url.rpartition('?see_lz=')
    url = s or e

    s, _, e = url.partition('tieba.baidu.com/p/')
    tid = e

    if not e:
        return

    # 获取帖子总页数
    headers = {'user-agent': USER_AGENT}
    r = session.get(url, headers=headers)
    text = r.text
    jq = PyQuery(text)
    pageCount = jq('#thread_theme_5 > div.l_thread_info > ul > li:nth-child(2) > span:nth-child(2)').text()
    pageCount = int(pageCount)
    tb_logger.info("tid: %s, 共%s页", tid, pageCount)

    # 获取帖子基本信息
    forum = jq('#container div.card_top > div.card_title > a.card_title_fname').text()
    title = jq('#j_core_title_wrap > h3').attr('title')
    data_field = jq('#j_p_postlist > div:nth-child(1)')[0].attrib['data-field']
    data_field = json.loads(data_field, encoding='utf-8')
    author = data_field['author']['user_name']

    tzObj = TiebaTiezi(tid, str(title), str(author), str(forum))

    # 获取每一页的内容
    for pageNum in range(1, pageCount + 1):
        pageUrl = '%s?pn=%s' % (url, pageNum)
        fetch_tiezi_single_page(tid, pageUrl, tzObj, headers)
        return tzObj


    # from tieba_model import TiebaData
    # from pprint import pprint

    # tzObj = TiebaData.get_instance().get_tiezi(tid)

    # print(tzObj.cell_count())
    # print(tzObj.deleted_cells())
    # tzObj.dump()

def check_is_ad_post(postElem):  # 检查是否是广告楼层
    import traceback
    from lxml.html import HtmlElement
    assert(isinstance(postElem, HtmlElement))

    attrib = postElem.attrib
    if 'data-field' not in attrib:
        return True

    postJQ = PyQuery(postElem)
    core_reply = postJQ('.core_reply')
    core_reply_text = core_reply.text().strip()
    if core_reply_text == '广告':
        return True

    data_field = attrib['data-field']

    try:
        json.loads(data_field)
    except:
        if data_field.find('{?=blockNum?}'):
            tb_logger.warning("广告楼层，data-field中有{?=blockNum?}")
            return True
        s = traceback.format_exc()
        tb_logger.error(s)
        return True

    return False


def fetch_tiezi_single_page(tid, pageUrl, tieziObj, headers):  # 获取单页帖子的内容
    assert(isinstance(tieziObj, TiebaTiezi))
    tb_logger.debug(pageUrl)

    r = session.get(pageUrl, headers=headers)
    text = r.text
    jq = PyQuery(text)
    postList = jq('#j_p_postlist > div')

    for post in postList:
        if check_is_ad_post(post):
            continue

        attrib = post.attrib
        postJQ = PyQuery(post)

        data_field = attrib['data-field']
        data_field = json.loads(data_field, object_pairs_hook=OrderedDict)
        # 创建楼层数据对象
        cell = TiebaCell.create(data_field)
        tieziObj.add_cell(cell)
        # print(cell.get_field('pb_tpoint'))

        extdata = OrderedDict()

        badge_title = postJQ('.d_badge_title')
        badge_lv = postJQ('.d_badge_lv')
        badge_title = badge_title.text()
        badge_lv = badge_lv.text()
        if not badge_title or not badge_lv:
            tb_logger.error('解析用户等级贴吧出错')
            print(postJQ.text())
            continue
        badge_lv = int(badge_lv)
        extdata['badge_title'] = badge_title
        extdata['badge_lv'] = badge_lv

        post_date = postJQ('div.post-tail-wrap > span:last-child')
        post_date = post_date.text()
        extdata['post_time'] = post_date

        cell.update_ext_data(extdata)

        fetch_lzl(tid, cell, headers)

    print(len(postList), '---')


def fetch_lzl(tid, cell, headers):  # 获取楼中楼
    assert(isinstance(cell, TiebaCell))
    comment_num = cell.get_field('comment_num', 'content')
    if comment_num is None:
        return
    try:
        comment_num = int(comment_num)
    except:
        comment_num = 0

    if comment_num <= 0:
        return

    pid = cell.get_field('post_id', 'content')
    comment_url = 'http://tieba.baidu.com/p/comment?tid=%s&pid=%s&pn=1' % (tid, pid)

    cmt_r = session.get(comment_url, headers=headers)
    cmt_text = cmt_r.text
    commentJQ = PyQuery(cmt_text)

    cmt_tail = commentJQ('li.lzl_li_pager.j_lzl_l_p.lzl_li_pager_s > p > a:last-child')
    cmtTotalPages = 1  # 楼中楼总页数
    if cmt_tail.text().strip() == '尾页':
        # todo: 优化获取楼中楼数量的方法
        cmtTotalPages = int(cmt_tail[0].attrib['href'][1:])

    comment_list = []

    for cmtPage in range(1, cmtTotalPages + 1):
        comment_url = 'http://tieba.baidu.com/p/comment?tid=%s&pid=%s&pn=%s' % (tid, pid, cmtPage)
        cmt_r = session.get(comment_url, headers=headers)
        cmt_text = cmt_r.text
        commentJQ = PyQuery(cmt_text)

        for single_cmt in commentJQ('li.lzl_single_post.j_lzl_s_p'):  # 遍历楼中楼的每一个评论
            single_cmt_jq = PyQuery(single_cmt)

            cmt_data_field = single_cmt.attrib.get('data-field')
            cmt_data_field = json.loads(cmt_data_field)
            username = cmt_data_field.get('user_name')
            spid = cmt_data_field.get('spid')
            portrait = cmt_data_field.get('portrait')
            user_href = single_cmt_jq('div > a')[0].attrib.get('href')

            lzl_content_main = single_cmt_jq('div > span.lzl_content_main')[0]
            content = PyQuery(lzl_content_main).html()

            lzl_time = single_cmt_jq('div > div > span.lzl_time').text()

            single_cmt_data = OrderedDict()

            single_cmt_data['username'] = username
            single_cmt_data['spid'] = spid
            single_cmt_data['portrait'] = portrait
            single_cmt_data['user_href'] = user_href
            single_cmt_data['content'] = content
            single_cmt_data['lzl_time'] = lzl_time
            lzl_obj = TiebaLZL.create(single_cmt_data)
            comment_list.append(lzl_obj)

    if comment_num != len(comment_list):
        tb_logger.error('楼中楼数量不匹配： %s, %s',  comment_num, len(comment_list))
        # print(postJQ.text())

    cell.update_comments(comment_list)


def fetch_post_tail():  # 获取小尾巴
    pass
