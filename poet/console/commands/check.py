# -*- coding: utf-8 -*-

from .command import Command


class CheckCommand(Command):
    """
    Check the <comment>poetry.toml</> file.

    check
    """

    def handle(self):
        self.line('')

        self.poet.check()

        self.info('The <comment>poetry.toml</> file is valid!')
