# -*- coding: utf-8 -*-

import os
import tempfile
import pytest

from cleo import CommandTester
from poet.console import Application
from poet.console.commands import InstallCommand as BaseCommand
from poet.poet import Poet as BasePoet
from pip.req.req_install import InstallRequirement

fd, DUMMY_LOCK = tempfile.mkstemp(prefix='poet_lock_')
os.close(fd)
os.unlink(DUMMY_LOCK)


class Poet(BasePoet):

    @property
    def lock_file(self):
        return DUMMY_LOCK

    @property
    def features(self):
        return {
            'my-feature': ['requests']
        }


class InstallCommand(BaseCommand):

    @property
    def poet_file(self):
        return os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'poetry.toml')

    @property
    def poet(self):
        return Poet(self.poet_file)

    def pip(self):
        return 'pip'

    def python(self):
        return 'python'


def test_install_default(mocker, check_output):
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    resolve.return_value = [InstallRequirement.from_line('pendulum==1.2.0')]
    reverse_dependencies.return_value = {}
    app = Application()
    app.add(InstallCommand())

    command = app.find('install')
    command_tester = CommandTester(command)
    command_tester.execute([('command', command.name), ('--no-progress', True)])

    assert os.path.exists(DUMMY_LOCK)
    os.remove(DUMMY_LOCK)

    output = command_tester.get_display()
    expected = """
Locking dependencies to poetry.lock

Resolving dependencies
Writing dependencies

Installing dependencies

 - Installing pendulum (1.2.0)
"""

    assert output == expected


def test_install_invalid_feature(app):
    app = Application()
    app.add(InstallCommand())

    command = app.find('install')
    command_tester = CommandTester(command)

    with pytest.raises(ValueError):
        command_tester.execute([
            ('command', command.name),
            ('--features', ['invalid']),
            ('--no-progress', True)
        ])

def test_install_already_installed_normal(app, check_output, mocker):
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    resolve.return_value = [
        InstallRequirement.from_line('requests==2.13.0'),
        InstallRequirement.from_editable('git+https://github.com/sdispater/cleo.git@d54cb993b2342e95ae4fce817af8a841c43514ef#egg=cleo'),
    ]
    reverse_dependencies.return_value = {}

    app = Application()
    app.add(InstallCommand())

    command = app.find('install')
    command_tester = CommandTester(command)
    output = command_tester.execute([
        ('command', command.name),
        ('--no-progress', True)
    ])

    expected = """
Installing dependencies
    
All dependencies already installed    
"""
