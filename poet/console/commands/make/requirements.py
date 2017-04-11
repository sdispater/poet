# -*- coding: utf-8 -*-

import os

from ....installer import Installer

from ..command import Command


TEMPLATE="""from setuptools import setup

kwargs = {}

setup(**kwargs)
"""


class MakeRequirementsCommand(Command):
    """
    Renders a requirements.txt file for testing purposes.

    make:requirements
        { --no-dev : Do not write dev dependencies }
    """

    def handle(self):
        installer = Installer(self, self._repository)

        deps = self._poet.pip_dependencies

        if not self.option('no-dev'):
            deps += self._poet.pip_dev_dependencies

        self.line('')
        packages = installer._resolve(deps)

        requirements = os.path.join(os.path.dirname(self.poet_file), 'requirements.txt')

        with open(requirements, 'w') as f:
            for package in packages:
                version = package['version']
                if isinstance(version, dict):
                    version = '-e {}@{}#egg={}'.format(version['git'], version['rev'], package['name'])
                else:
                    version = '{}=={}'.format(package['name'], version)

                f.write(version + '\n')
