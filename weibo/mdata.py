# -*- coding: utf-8 -*-
import enum
from enum import Enum
from weibo import filedriver


@enum.unique
class EType(Enum):
    int = 1
    str = 2


g_users = {}


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
        if name not in self.config_dict:
            raise Exception(f'no filed {name}')
        self.data[name] = value

    def equal(self, obj:Data):
        pass


class Pic(Data):
    pass


class Blog(Data):
    def __init__(self):
        Data.__init__(self)
        config = [('itemid', str), ('scheme', str), ('mblog', Blog)]
        self.init(config)
attitudes_count

class Card(Data):
    def __init__(self):
        Data.__init__(self)
        config = [('itemid', str), ('scheme', str), ('mblog', Blog)]
        self.init(config)

    def load(self, card):
        pass

    def dump(self, card):
        pass


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
        pass
        # filedirver =


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
