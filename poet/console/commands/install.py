# -*- coding: utf-8 -*-

from ...installer import Installer

from .command import Command


class InstallCommand(Command):
    """
    Install and lock dependencies specified in poetry.toml file.

    install
        {--no-dev : Do not install dev dependencies}
    """

    def handle(self):
        dev = not self.option('no-dev')

        installer = Installer(self, self._repository)

        if self.has_lock():
            poet = self.poetry.lock
        else:
            poet = self.poet

        installer.install(poet, dev=dev)
