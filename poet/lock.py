# -*- coding: utf-8 -*-

from .package import PipDependency
from .poet import Poet


class Lock(Poet):

    def is_lock(self):
        return True

    def load(self):
        root = self._config['root']
        self._name = root['name']
        self._version = root['version']

        packages = self._config['package']

        self._dependencies = []
        for package in packages:
            dep = PipDependency(package['name'], package['version'], package['checksum'])

            self._dependencies.append(dep)

