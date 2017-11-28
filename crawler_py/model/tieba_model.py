# -*- coding: utf-8 -*-

import json
import os
from pprint import pprint
from collections import ChainMap, OrderedDict

import psycopg2

from common.common import Singleton


class TiebaData(Singleton):
    def __init__(self):
        pass

    def get_tiezi(self, tid):
        dirname = './.data.d/%s' % tid
        if os.path.exists(dirname):
            pass
        else:
            os.makedirs(dirname)

        tiezi = TiebaTiezi(tid)
        return tiezi


class TiebaTiezi(object):
    ''' tiezi '''
    def __init__(self, tid, title='', author='', forum=''):
        self.tid = tid
        self.title = title
        self.author = author
        self.forum = forum
        self.cells = []

        print(tid, title, author, forum)

    def add_cell(self, cell):
        assert(isinstance(cell, TiebaCell))
        self.cells.append(cell)

    def get_deleted_cells(self):  # 已被删除的楼层
        nums = [int(x.get_field('post_no')) for x in self.cells]
        max_num = max(nums)
        return list(filter(lambda x: x not in nums, range(1, max_num + 1)))

    def cell_count(self):
        return len(self.cells)

    def update(self, tzObj):
        assert(isinstance(tzObj, TiebaTiezi))
        pass

    def serial(self):
        data = [x.serial() for x in self.cells]
        tiezi_data = {
            'tid': self.tid,
            'title': self.title,
            'author': self.author,
            'forum': self.forum,
            'cells': data,
        }
        return tiezi_data

    def dump(self, driver, origin_driver=None):  # 从origin_driver获取上一次的数据
        from driver.driver import TiebaDriver
        assert(isinstance(driver, TiebaDriver))

        tiezi_data = driver.get_tiezi_data(self.tid)
        if tiezi_data:
            old_tiezi_obj = TiebaTiezi.create(tiezi_data)
            old_tiezi_obj.update(self)
            driver.save(old_tiezi_obj.serial())
        else:
            driver.save(self.serial())

    @staticmethod
    def create(tiezi_data):
        tid = tiezi_data['tid']
        title = tiezi_data['title']
        author = tiezi_data['author']
        forum = tiezi_data['forum']
        cells = tiezi_data['cells']

        tzObj = TiebaTiezi(str(tid), str(title), str(author), str(forum))
        for cell_data in cells:
            cell_obj = TiebaCell.create(cell_data)
            tzObj.add_cell(cell_obj)
        return tzObj


class TiebaCell(object):  # 帖子的楼层
    def __init__(self):
        self.author_data = OrderedDict()
        self.content_data = OrderedDict()
        self.comments = []  # 楼中楼
        self.ext_data = OrderedDict()

    def get_field(self, field, major=None):
        if major == 'author':
            return self.author_data.get(field)
        elif major == 'content':
            return self.content_data.get(field)
        elif major == 'ext':
            return self.ext_data.get(field)
        else:
            return ChainMap(self.author_data, self.content_data, self.ext_data).get(field)

    def update_author_data(self, author_data):
        for k, v in author_data.items():
            self.author_data[k] = v

    def update_content_data(self, content_data):
        for k, v in content_data.items():
            self.content_data[k] = v

    def update_comments(self, comment_list):
        # todo: 合并的情况
        self.comments = comment_list

    def update_ext_data(self, ext_data):
        for k, v in ext_data.items():
            self.ext_data[k] = v

    def serial(self):
        data = OrderedDict()
        data['author'] = self.author_data
        data['content'] = self.content_data
        data['comments'] = [c.serial() for c in self.comments]
        data['ext'] = self.ext_data
        return data

    @staticmethod
    def create(cell_data):
        cell_obj = TiebaCell()
        author_data = cell_data.get('author')
        content_data = cell_data.get('content')
        comments = cell_data.get('comments')
        ext_data = cell_data.get('ext')
        if author_data:
            cell_obj.update_author_data(author_data)
        if content_data:
            cell_obj.update_content_data(content_data)
        if comments:
            cell_obj.update_comments([TiebaLZL.create(d) for d in comments])
        if ext_data:
            cell_obj.update_ext_data(ext_data)
        return cell_obj


class TiebaLZL(object):  # 楼中楼
    def __init__(self):
        self.data = OrderedDict()

    def update(self, lzl_data):
        for k, v in lzl_data.items():
            self.data[k] = v

    def serial(self):
        return self.data

    @staticmethod
    def create(lzl_data):
        lzl_obj = TiebaLZL()
        if lzl_data:
            lzl_obj.update(lzl_data)
        return lzl_obj


class TiebaUserCenter(Singleton):
    def __init__(self, arg):
        self.m_users = {}
        pass


class TiebaUser(object):
    def __init__(self, arg):
        pass


class TiebaForumCenter(Singleton):
    def __init__(self, arg):
        self.m_forums = {}


class TiebaForum(object):
    def __init__(self, arg):
        self.forum = ''
        self.m_badgeDict = {}











class TiebaBookmarkModel(Singleton):
    def __init__(self):
        pass

        with open('tieba-favors.json', 'r') as f:
            data = json.load(f)
            # print(data)
            for item in data:
                print(item)

    def add_bookmark(self, bookmark_data):  # bookmark_data:dict
        pass

    def get_forums(self):
        pass

    def get_bookmarks(self, forum=None):
        pass

    def count(self, forum=None):
        pass
