# -*- coding: utf-8 -*-

import os
import tempfile

from cleo import CommandTester


def test_default(app, mocker, tmp_dir):
    getcwd = mocker.patch('os.getcwd')
    getcwd.return_value = tmp_dir

    command = app.find('init')
    tester = CommandTester(command)
    tester.set_inputs([
        'my-package',  # Package name
        '',  # Version
        'This is a description',  # Description
        'n',  # Author
        'MIT',  # License
        'n',  # Interactive packages
        'n',  # Interactive dev packages
        '\n'  # Generate
    ])
    tester.execute([('command', command.name)])

    output = tester.get_display()
    expected = """
Generated file

[package]
name = "my-package"
version = "0.1.0"
description = "This is a description"
license = "MIT"



Do you confirm generation [yes]? 
"""

    assert expected in output
    assert os.path.exists(os.path.join(tmp_dir, 'poetry.toml'))
