# -*- coding:utf-8 -*-
'''
Created on 2017年5月30日

@author: jia
'''
import os
import time
import difflib
from functools import wraps
import colorama

colorama.init(autoreset=True)


def env(name):
    value = os.environ[name]
    value = value.strip()
    if value.startswith('\'') and value.startswith('\''):
        value = value[1:-1]
    if value.startswith('\"') and value.startswith('\"'):
        value = value[1:-1]
    if os.path.isdir(value) or os.path.isfile(value) or os.path.isabs(value):
        assert(os.path.isabs(value))
        value = os.path.normpath(value)
    return value


def file_diff(fromfile, tofile, options=None):
    '''
    Get the difference between two files
    '''
    fromData = []
    with open(fromfile, 'r') as fd:
        fromData = fd.readlines()
    toData = []
    with open(tofile, 'r') as fd:
        toData = fd.readlines()
    fromBaseName = os.path.basename(fromfile)
    toBaseName = os.path.basename(tofile)

    if options == 'u':
        result = difflib.unified_diff(fromData, toData, fromfile=fromBaseName, tofile=toBaseName)
    elif options == 'n':
        result = difflib.ndiff(fromData, toData)
    elif options == 'm':
        result = difflib.HtmlDiff().make_file(fromData, toData, fromBaseName, toBaseName)
    else:
        result = difflib.context_diff(fromData, toData, fromfile=fromBaseName, tofile=toBaseName)

    return result


def print_diff(diff):
    for line in diff:
        if line.startswith('!'):
            print(colorama.Fore.RED + line.rstrip())
        else:
            print(line.rstrip())


def fcopy(src_path, des_path):
    with open(src_path, 'r') as fd:
        data = fd.read()
    with open(des_path, 'w') as fd:
        fd.write(data)


def file_normalize(filename):
    with open(filename, 'r') as fd:
        data = fd.readlines()
    data = [line.rstrip() for line in data]
    data = [l.replace('\t', ' ' * 4) for l in data]
    text = '\n'.join(data) + '\n'
    with open(filename, 'w') as fd:
        fd.write(text)


def timethis(logger=None):
    '''
    Decorator that reports the execution time.
    '''
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            summary = '%s %s: %s' % (func.__name__, '耗时', end - start)
            if logger:
                logger(summary)
            else:
                print(summary)
            return result
        return wrapper
    return decorate


def split(seq, condition):
    result = []
    s = []
    for l in seq:
        if condition(l):
            if s:
                result.append(s)
                s = []
        s.append(l)
    if s:
        result.append(s)
    return result
