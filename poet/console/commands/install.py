# -*- coding: utf-8 -*-

from ...installer import Installer

from .command import Command


class InstallCommand(Command):
    """
    Install and lock dependencies specified in the <comment>poetry.toml</comment> file.

    install
        { --f|features=* : Features to install. }
        { --no-dev : Do not install dev dependencies. }
        { --no-progress : Do not output download progress. }
    """

    def handle(self):
        features = []
        for feature in self.option('features'):
            if ' ' in feature:
                features += [f.replace('_', '-').lower() for f in feature.split(' ')]
            else:
                features.append(feature.replace('_', '-').lower())

        dev = not self.option('no-dev')

        installer = Installer(
            self, self._repository,
            with_progress=not self.option('no-progress')
        )

        installer.install(features=features, dev=dev)
