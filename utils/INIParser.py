# -*- coding: utf-8 -*-
import logging

from utils import utils

logger = logging.getLogger('crawler')


class Data(object):
    def __init__(self):
        self.__dict__["data"] = {}

    def __setattr__(self, name, value):
        self.__dict__["data"][name] = value

    def __getattr__(self, name):
        try:
            return self.__dict__["data"][name]
        except Exception:
            raise Exception(f'no field[{name}]')

    def __repr__(self):
        return f'Data{str(self.__dict__["data"])}'


class Section(object):
    def __init__(self, stype):
        pass

class INI(object):
    def __init__(self, parent=None:INI):
        self.data = {}
        # self.parent = None
        # self.tag = None
        # self.fi

    def __getitem__(self, name):
        if self.parent is not None:
            return self.parent[name]
        return self.data[name]

    def __setitem__(self, name, value):
        if self.parent is not None:
            self.parent[name] = value
            return
        self.data[name] = value
    
    # def sub(self, subname):
    #     for key in self.data.keys():
    #         pass
    #         if key.startswith(f'{subname}.'):
    #             pass
    #     d=self[dd]


class INIParser(object):
    def __init__(self, content):
        self.parser(content)

    def parser(self, content:str):
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        lines = [l for l in lines if not l.startswith(';')]
        section_list = utils.split(lines, lambda l: l.startswith('[') and l.endswith(']'))
        ini = INI()
        for s in section_list:
            self.parser_section(ini, s)
        # print(content)
        # logger.info(section_list)
        print(ini)

    def parser_section(self, ini, lines):
        header = lines[0]
        lines = lines[1:]
        stype, header = self.parser_header(header)
        ini[header] = self.parser_section_body(stype, lines)
        logger.info(stype)
        logger.info(header)
        logger.info(lines)

    def parser_header(self, header):
        header = header[1:-1].strip()
        z = [x.strip() for x in header.split(' ') if x.strip()]
        if len(z) >= 2:
            stype = z[0]
            header = z[1]
        else:
            stype = 'dict'
            header = z[0]
        return stype, header

    def parser_section_body(self, stype, lines):
        data = None
        if stype == 'dict':
            data = {}
            tmp = [l.partition('=') for l in lines]
            tmp = [(x[0].strip(), x[2].strip()) for x in tmp]
            for (k, v) in tmp:
                data[k] = v  # 暂时全部用字符串比较安全
        elif stype == 'list':
            data = lines
        else:
            raise Exception('unsupported type')
        return data

    def parser_value(self, key, value):
        if value == '':
            raise Exception(f'[{key}] miss value')
        elif value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif utils.is_float(value):
            value = float(value)
        return value

    @staticmethod
    def read(filename):
        obj = None
        with open(filename, 'rt', encoding='utf8') as fd:
            text = fd.read()
            obj = INIParser(text)
        return obj
