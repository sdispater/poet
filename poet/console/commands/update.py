# -*- coding: utf-8 -*-

from ...installer import Installer

from .command import Command


class UpdateCommand(Command):
    """
    Update dependencies as according to the <comment>poetry.toml</> file.

    update
        { packages?* : The packages to update }
        { --f|features=* : Features to install }
    """

    def handle(self):
        if not self.has_lock():
            # We do not have a lock file
            # Assuming installation
            return self.call('install', [('--features', self.option('features'))])

        features = []
        for feature in self.option('features'):
            if ' ' in feature:
                features += [f.replace('_', '-').lower() for f in feature.split(' ')]
            else:
                features.append(feature.replace('_', '-').lower())

        installer = Installer(self, self._repository)

        installer.update(packages=self.argument('packages'), features=features)
