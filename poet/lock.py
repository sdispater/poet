# -*- coding: utf-8 -*-

from .package import PipDependency, Dependency
from .poet import Poet


class Lock(Poet):

    def is_lock(self):
        return True

    def load(self):
        root = self._config['root']
        self._name = root['name']
        self._version = root['version']

        packages = self._config['package']

        for package in packages:
            dep = Dependency(
                package['name'],
                package['version'],
                optional=package.get('optional')
            )
            pip_dep = PipDependency(
                package['name'],
                package['version'],
                category=package['category'],
                optional=package.get('optional'),
                checksum=package.get('checksum')
            )

            if package['category'] == 'dev':
                self._dev_dependencies.append(dep)
                self._pip_dev_dependencies.append(pip_dep)
            else:
                self._dependencies.append(dep)
                self._pip_dependencies.append(pip_dep)

        self._features = self._config.get('features', {})
