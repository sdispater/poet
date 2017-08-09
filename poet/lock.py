# -*- coding: utf-8 -*-

from semantic_version import Version

from .package import PipDependency, Dependency
from .poet import Poet, InvalidElement


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

        self._features = self._get_features()

    def check(self):
        root = self._config.get('root')
        if not root:
            raise RuntimeError(
                'Invalid lock file. '
                'Please regenerate it with: poet lock -f'
            )

        if 'name' not in root or 'version' not in root:
            raise RuntimeError(
                'Invalid lock file. '
                'Please regenerate it with: poet lock -f'
            )

        packages = self._config.get('package')
        if packages:
            for package in packages:
                self._check_package_constraint(
                    package['name'], package['version']
                )

    def _check_package_constraint(self, name, constraint):
        message = 'Invalid constraint [{}]'.format(constraint)

        if isinstance(constraint, dict):
            return self._check_vcs_constraint(name, constraint)
        else:
            try:
                return Version.coerce(constraint)
            except ValueError:
                pass

        raise InvalidElement('package.{}'.format(name), message)
