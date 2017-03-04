# -*- coding: utf-8 -*-

from ...installer import Installer

from .command import Command


class LockCommand(Command):
    """
    Lock the dependencies set in sonnet.toml.

    lock
    """

    def handle(self):
        if self.has_lock():
            return

        installer = Installer(self, self._repository)

        installer.lock(self.sonnet)
