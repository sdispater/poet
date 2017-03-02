# -*- coding: utf-8 -*-

from .command import Command


class CheckCommand(Command):
    """
    Check the sonnet.toml file.

    check
    """

    def handle(self):
        self.line('')

        self.sonnet.check()

        self.info('The <comment>sonnet.toml</> file is valid!')
