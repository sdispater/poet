# -*- coding: utf-8 -*-

from ...installer import Installer

from .index_command import IndexCommand


class InstallCommand(IndexCommand):
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
                features += feature.split(' ')
            else:
                features.append(feature)

        dev = not self.option('no-dev')

        installer = Installer(
            self, self._repository,
            with_progress=not self.option('no-progress')
        )

        installer.install(features=features, dev=dev)
