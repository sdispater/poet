# -*- coding: utf-8 -*-

import re
from .utils.helpers import call


class GitConfig(object):

    def __init__(self):
        config_list = call(['git', 'config', '-l'])

        self._config = {}

        m = re.findall('(?ms)^([^=]+)=(.*?)$', config_list)
        if m:
            for group in m:
                self._config[group[0]] = group[1]

    def get(self, key, default=None):
        return self._config.get(key, default)

    def __getitem__(self, item):
        return self._config[item]
