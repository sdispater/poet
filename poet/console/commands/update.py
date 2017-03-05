# -*- coding: utf-8 -*-

from ...installer import Installer

from .command import Command


class UpdateCommand(Command):
    """
    Update dependencies has according to the poetry.toml file.

    update
    """

    def handle(self):
        if not self.has_lock():
            # We do not have a lock file
            # Assumming installation
            return self.call('install')

        installer = Installer(self, self._repository)

        installer.install(self.poet)
