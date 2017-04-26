# -*- coding: utf-8 -*-

import os
import shutil

from cleo.testers import CommandTester
from pip.req.req_install import InstallRequirement
from poet.poet import Poet


def test_command(app, mocker, tmp_dir):
    poetry_file = os.path.join(tmp_dir, 'poetry.toml')
    readme = os.path.join(tmp_dir, 'README.rst')
    fixtures = os.path.join(os.path.dirname(__file__), '..', 'fixtures')
    shutil.copy(os.path.join(fixtures, 'poetry.toml'), poetry_file)
    shutil.copy(os.path.join(fixtures, 'README.rst'), readme)
    requirements_file = os.path.join(tmp_dir, 'requirements.txt')

    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    resolve.return_value = [InstallRequirement.from_line('pendulum==1.2.0')]
    reverse_dependencies.return_value = {}
    poet = Poet(poetry_file)
    poet_prop = mocker.patch('poet.console.commands.command.Command.poet', poet)
    poet_prop.return_value = poet

    command = app.find('make:requirements')
    tester = CommandTester(command)
    tester.execute([('command', command.name)])

    expected = """
 - Resolving dependencies
 - Created requirements.txt file
"""

    output = tester.get_display()

    assert expected == output

    assert os.path.exists(requirements_file)

    content = """pendulum==1.2.0
"""

    with open(requirements_file) as f:
        assert content == f.read()

