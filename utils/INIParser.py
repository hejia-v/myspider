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


class INI(Data):
    def __init__(self):
        Data.__init__(self)

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)


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
                if v == '':
                    raise Exception(f'[{k}] miss value')
                elif v.lower() == 'true':
                    v = True
                elif v.lower() == 'false':
                    v = False
                pass
        elif stype == 'list':
            pass
        else:
            raise Exception('unsupported type')
        return data

    @staticmethod
    def read(filename):
        obj = None
        with open(filename, 'rt', encoding='utf8') as fd:
            text = fd.read()
            obj = INIParser(text)
        return obj
