# -*- coding: utf-8 -*-


class Singleton(object):
    _instance = None

    @classmethod
    def get_instance(cls, *arg, **karg):
        if cls._instance is None:
            cls._instance = cls(*arg, **karg)
        return cls._instance

