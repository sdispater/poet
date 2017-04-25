# -*- coding: utf-8 -*-

import os
import pytest
from cleo import CommandTester


def test_lock(app, mocker):
    base_dir = os.path.join(
        os.path.dirname(__file__), '..', '..', 'examples', 'basic'
    )
    lock = os.path.join(base_dir, 'poetry.lock')
    if os.path.exists(lock):
        os.unlink(lock)

    getcwd = mocker.patch('os.getcwd')
    getcwd.return_value = base_dir
    command = app.find('lock')
    command_tester = CommandTester(command)
    command_tester.execute([('command', command.name), ('--no-progress', True)])

    output = command_tester.get_display()
    expected = """
Locking dependencies to poetry.lock

 - Resolving dependencies
 - Writing dependencies
"""

    assert expected == output
