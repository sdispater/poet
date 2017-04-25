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
            constraint = {
                'optional': package.get('optional', False),
                'python': package.get('python', ['*'])
            }
            version = package['version']
            if isinstance(version, dict):
                constraint.update(version)
            else:
                constraint['version'] = version

            dep = Dependency(
                package['name'],
                constraint,
                category=package['category']
            )
            pip_dep = PipDependency(
                package['name'],
                constraint,
                category=package['category'],
                checksum=package.get('checksum')
            )

            if package['category'] == 'dev':
                self._dev_dependencies.append(dep)
                self._pip_dev_dependencies.append(pip_dep)
            else:
                self._dependencies.append(dep)
                self._pip_dependencies.append(pip_dep)

        self._features = self._config.get('features', {})
