# -*- coding: utf-8 -*-

from urllib.parse import urlparse
from common.common import Singleton


class BookmarkModel(Singleton):
    def __init__(self):
        pass

    def add_bookmark(self, url, extra=None):
        url = url or ""
        url = url.strip()
        if not url:
            return
        pass
        # print(line)
        url = urlparse(url)
        # print(url)
        print(url.hostname)


