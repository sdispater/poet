# -*- coding: utf-8 -*-

import os
import toml
import twine.utils

from .utils.helpers import template, mkdir_p
from .locations import CONFIG_DIR, CACHE_DIR


class Config(object):


    def __init__(self, poet):
        if not os.path.exists(os.path.join(CONFIG_DIR, 'config.toml')):
            self._create()

        with open(os.path.join(CONFIG_DIR, 'config.toml')) as f:
            self._config = toml.loads(f.read())

        self._config.update({
            'home': CONFIG_DIR,
            'cache_dir': CACHE_DIR
        })

    def get(self, key):
        split_key = key.split('.')
        current = self._config

        return self._get(current, split_key)

    def all(self):
        return self._config

    def _get(self, content, keys):
        if not keys:
            return content

        if not isinstance(content, dict):
            if keys:
                raise ValueError('Invalid config key')

            return content

        key = keys.pop(0)
        if key not in content:
            raise ValueError('Invalid config key')

        content = content[key]

        return self._get(content, keys)

    def _create(self):
        config_file = os.path.join(CONFIG_DIR, 'config.toml')

        mkdir_p(CONFIG_DIR)

        # Try to load default ~/.pypirc file to transfer
        path = os.path.expanduser('~/.pypirc')
        if not os.path.exists(path):
            config = self._get_default_config()
        else:
            pypirc_config = twine.utils.get_config()

            repositories = []
            for repository, settings in pypirc_config.items():
                repositories.append({
                    'name': repository,
                    'url': settings.get('repository', 'https://pypi.python.org/pypi'),
                    'username': settings.get('username'),
                    'password': settings.get('password'),
                })

            config = {
                'repositories': repositories
            }

        with open(config_file, 'w') as f:
            f.write(template('config.toml').render(**config))

    def _get_default_config(self):
        return {
            'repositories': [
                {'name': 'pypi', 'url': 'https://pypi.python.org/pypi'}
            ]
        }
