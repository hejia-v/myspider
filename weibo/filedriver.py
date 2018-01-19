# -*- coding: utf-8 -*-
import os
import json
from collections import OrderedDict
from utils import utils


g_weibo_data_dir = utils.get_path_with_base_file(__file__, '../data/weibo')


def read_json_file(uid):
    filename = os.path.join(g_weibo_data_dir, f'{uid}.json')
    data = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
    return data


def write_json_file(uid, data):
    filename = os.path.join(g_weibo_data_dir, f'{uid}.json')
    if not os.path.exists(g_weibo_data_dir):
        os.mkdir(g_weibo_data_dir)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def add_card(uid, card_data):
    data = read_json_file(uid)
    data.append(card_data)
    write_json_file(uid, data)
