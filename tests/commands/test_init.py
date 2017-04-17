# -*- coding: utf-8 -*-

import os
import tempfile

from cleo import CommandTester


def test_basic_interactive(app, mocker, tmp_dir, check_output):
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
    expected = command.template('poetry.toml').render(
        name='my-package',
        version='0.1.0',
        description='This is a description',
        authors=[],
        license='MIT'
    )

    assert expected in output
    assert os.path.exists(os.path.join(tmp_dir, 'poetry.toml'))
    check_output.assert_called_once()


def test_default_template(app, mocker, tmp_dir):
    getcwd = mocker.patch('os.getcwd')
    getcwd.return_value = tmp_dir

    command = app.find('init')
    tester = CommandTester(command)
    tester.execute([('command', command.name), ('template', 'default')])

    output = tester.get_display()
    content = command.template('poetry.toml').render()
    expected = """
                                        
  Welcome to the Poet config generator  
                                        


Using default template to create your poetry.toml config.

"""

    assert expected == output
    assert os.path.exists(os.path.join(tmp_dir, 'poetry.toml'))

    with open(os.path.join(tmp_dir, 'poetry.toml')) as f:
        assert content == f.read()
