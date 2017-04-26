# -*- coding: utf-8 -*-

import os

from ....installer import Installer

from ..index_command import IndexCommand


class MakeRequirementsCommand(IndexCommand):
    """
    Renders a requirements.txt file for testing purposes.

    make:requirements
        { --no-dev : Do not write dev dependencies }
    """

    def handle(self):
        installer = Installer(self, self._repository)

        deps = self.poet.pip_dependencies

        if not self.option('no-dev'):
            deps += self.poet.pip_dev_dependencies

        self.line('')
        packages = installer.resolve(deps)

        requirements = os.path.join(self.poet.base_dir, 'requirements.txt')

        with open(requirements, 'w') as f:
            for package in packages:
                version = package['version']
                if isinstance(version, dict):
                    version = '-e {}@{}#egg={}'.format(version['git'], version['rev'], package['name'])
                else:
                    version = '{}=={}'.format(package['name'], version)

                f.write(version + '\n')

        self.line(' - Created <info>requirements.txt</> file')
