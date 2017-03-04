# -*- coding: utf-8 -*-

from cleo import Command


class AboutCommand(Command):
    """
    Short information about Poet.

    about
    """

    def handle(self):
        self.line("""<info>Poet - Package Management for Python</info>

<comment>Poet is a dependency manager tracking local dependencies of your projects and libraries.
See <fg=blue>https://github.com/sdispater/poet</> for more information.</comment>
""")
