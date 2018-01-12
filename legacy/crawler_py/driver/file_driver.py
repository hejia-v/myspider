# -*- coding: utf-8 -*-
from driver.driver import TiebaDriver


class TiebaFileDriver(TiebaDriver):
    def __init__(self):
        TiebaDriver.__init__(self)

    def get_tiezi_data(self, tid):
        return {}

    def save(self, tiezi_data):
        pass
