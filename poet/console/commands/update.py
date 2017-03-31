# -*- coding: utf-8 -*-

from ...installer import Installer

from .command import Command


class UpdateCommand(Command):
    """
    Update dependencies as according to the <comment>poetry.toml</> file.

    update
    """

    def handle(self):
        if not self.has_lock():
            # We do not have a lock file
            # Assuming installation
            return self.call('install')

        installer = Installer(self, self._repository)

        installer.update()
