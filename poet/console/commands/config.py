# -*- coding: utf-8 -*-

import os
import re
import json

import toml

from ...locations import CONFIG_DIR
from ...config import Config

from .command import Command


class ConfigCommand(Command):
    """
    Set config options.
    
    config
        { setting-key? : Setting key }
        { setting-value?* : Setting value }
        { --list : List configuration settings }
        { --unset : Unset configuration setting }
    """

    SECRET_KEYS = (
        '^.*password.*$',
    )

    def handle(self):
        config = Config(self.poet)

        # List the configuration of the file settings
        if self.option('list'):
            self._display(config.all())

            return 0

        key = self.argument('setting-key')
        value = self.argument('setting-value')

        if value and self.option('unset'):
            raise RuntimeError('You can not combine a setting value with --unset')

        # show the value if no value is provided
        if not value and not self.option('unset'):
            m = re.match('^repos?(?:itories)?(?:\.(.+))?', key)
            if m:
                key = ['repositories']
                if m.group(1):
                    key += m.group(1).split()

                key = '.'.join(key)

            config_value = config.get(key)

            self._display(config_value, key.split('.'))

            return 0

    def _display(self, content, k=None):
        if not isinstance(content, dict):
            if k and self._is_secret('.'.join(k)):
                content = '********'

            if k:
                self.line('[<comment>{}</>] <info>{}</>'.format('.'.join(k), content))
            else:
                self.line('<info>{}</>'.format(content))

            return

        for key, value in content.items():
            if k:
                raw_key = k[:] + [key]
            else:
                raw_key = [key]

            if isinstance(value, dict):
                self._display(value, k=raw_key)

                continue

            if isinstance(value, list):
                value = list(map(json.dumps, value))

                value = '[{}]'.format(', '.join(value))

            self._display(value, raw_key)

    def _is_secret(self, key):
        for secret_key in self.SECRET_KEYS:
            if re.match(secret_key, key):
                return True

        return False

