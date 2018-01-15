# -*- coding: utf-8 -*-
import logging

from utils import utils

logger = logging.getLogger('crawler')


class Section(object):
    def __init__(self, stype):
        pass


class INI(object):
    def __init__(self):
        self.data = {}

    def __getitem__(self, name):
        return self.data[name]

    def __setitem__(self, name, value):
        self.data[name] = value

    def __repr__(self):
        return f'INI{self.data}'


class INIParser(object):
    def __init__(self):
        pass

    def parser(self, content:str):
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        lines = [l for l in lines if not l.startswith(';')]
        section_list = utils.split(lines, lambda l: l.startswith('[') and l.endswith(']'))
        ini = INI()
        for s in section_list:
            self.parser_section(ini, s)
        logger.info(ini)
        return ini

    def parser_section(self, ini, lines):
        header = lines[0]
        lines = lines[1:]
        stype, header = self.parser_header(header)
        ini[header] = self.parser_section_body(stype, lines)

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
        if stype == 'dict':
            data = {}
            tmp = [l.partition('=') for l in lines]
            tmp = [(x[0].strip(), x[2].strip()) for x in tmp]
            for (k, v) in tmp:
                data[k] = self.parser_value(k, v)
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
        with open(filename, 'rt', encoding='utf8') as fd:
            text = fd.read()
            parser = INIParser()
            ini = parser.parser(text)
        return ini
