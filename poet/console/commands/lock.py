# -*- coding: utf-8 -*-

from ...installer import Installer

from .command import Command


class LockCommand(Command):
    """
    Lock the dependencies specified in <comment>poetry.toml</comment>.

    lock
        {--f|force : Force locking}
        { --no-progress : Do not output download progress. }
    """

    def handle(self):
        if self.has_lock() and not self.option('force'):
            return

        installer = Installer(
            self, self._repository,
            with_progress=not self.option('no-progress')
        )

        installer.lock(self.poet)
