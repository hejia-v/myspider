# -*- coding: utf-8 -*-
import enum
from enum import Enum
from collections import OrderedDict
from weibo import filedriver


@enum.unique
class EType(Enum):
    int = 1
    str = 2
    bool = 3
    pic_list = 4
    blog = 5


g_users = {}


def base_type_factory(v, v_type):
    bsucc = True
    if v_type == EType.int:
        v = int(v)
    elif v_type == EType.str:
        v = str(v)
    elif v_type == EType.bool:
        v = bool(v)
    else:
        bsucc = False
    return bsucc, v


def serialize(v, v_type):
    bsucc, v = base_type_factory(v, v_type)
    if bsucc:
        return v
    if v_type == EType.pic_list:
        t = []
        for pic in v:
            t.append(pic.dump())
        v = t
    elif v_type == EType.blog:
        v = v.dump()
    else:
        raise Exception(f'unsupported type: {v_type}')
    return v


def unserialize(v, v_type):
    bsucc, v = base_type_factory(v, v_type)
    if bsucc:
        return v
    if v_type == EType.pic_list:
        t = []
        for pic_data in v:
            pic = Pic()
            pic.load(pic_data)
            t.append(pic)
        v = t
    elif v_type == EType.blog:
        blog = Blog()
        blog.load(v)
        v = blog
    else:
        raise Exception(f'unsupported type: {v_type}')
    return v


class Data(object):
    def __init__(self):
        self.config = []
        self.config_dict = {}
        self.data = {}

    def init(self, config):
        self.config = config
        self.config_dict = dict(config)
        self.data = {}

    def __getitem__(self, name):
        if name not in self.config_dict:
            raise Exception(f'no filed {name}')
        return self.data[name]

    def __setitem__(self, name, value):
        self.data[name] = value

    def load(self, data:dict):
        for (key, value_type) in self.config:
            if key in data:
                v = data[key]
                v = unserialize(v, value_type)
                self.data[key]=v

    def dump(self):
        d = OrderedDict()
        for (key, value_type) in self.config:
            if key in self.data:
                v = self.data[key]
                v = serialize(v, value_type)
            else:
                v = None
            d[key] = v
        return d

    def equal(self, obj):
        pass


class Pic(Data):
    def __init__(self):
        Data.__init__(self)
        config = [
            ('pid', EType.str),
            ('size', EType.str),
            ('url', EType.str),
        ]
        self.init(config)

    def load(self, data:dict):
        self.data['pid'] = data['pid']
        self.data['size'] = data['large']['size']
        self.data['url'] = data['large']['url']


class Blog(Data):
    def __init__(self):
        Data.__init__(self)
        config = [
            ('attitudes_count',  EType.int),
            ('comments_count', EType.int),
            ('content_auth', EType.int),
            ('reposts_count', EType.int),
            ('created_at', EType.str),
            ('bid', EType.str),
            ('id', EType.str),
            ('idstr', EType.str),
            ('mid', EType.str),
            ('isLongText', EType.bool),
            ('is_paid', EType.bool),
            ('mblogtype', EType.int),
            ('original_pic', EType.str),
            ('pics', EType.pic_list),
            ('source', EType.str),
            ('text', EType.str),
            ('textLength', EType.int),
        ]
        self.init(config)


class Card(Data):
    def __init__(self):
        Data.__init__(self)
        config = [
            ('itemid', EType.str),
            ('scheme', EType.str),
            ('mblog', EType.blog),
        ]
        self.init(config)


class User(object):
    def __init__(self, uid):
        self.uid = uid
        self.cards= []

    def add_card_list(self, card_list: list):
        for card_data in card_list:
            print(card_data)
            card = Card()
            card.load(card_data)
            self.cards.append(card)
        return True

    def dump(self):
        t = []
        for card in self.cards:
            t.append(card.dump())
        filedriver.write_json_file(self.uid, t)


def add_card_list_data(uid,card_list:list):
    global g_users
    if uid not in g_users:
        user = User(uid)
        g_users[uid] = user
    else:
        user = g_users[uid]
    bsucc = user.add_card_list(card_list)
    user.dump()
    return bsucc
