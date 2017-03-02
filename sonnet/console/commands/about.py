# -*- coding: utf-8 -*-

from cleo import Command


class AboutCommand(Command):
    """
    Short information about Sonnet.

    about
    """

    def handle(self):
        self.line("""<info>Sonnet - Package Management for Python</info>

<comment>Sonnet is a dependency manager tracking local dependencies of your projects and libraries.
See <fg=blue>https://github.com/sdispater/sonnet</> for more information.</comment>
""")
