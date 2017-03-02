# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

from sonnet.console import Application
from cleo import CommandTester


def test_output():
    app = Application()

    command = app.find('about')
    command_tester = CommandTester(command)
    command_tester.execute([('command', command.get_name())])

    assert """Sonnet - Package Management for Python

Sonnet is a dependency manager tracking local dependencies of your projects and libraries.
See https://github.com/sdispater/sonnet for more information.

""" == command_tester.get_display()

