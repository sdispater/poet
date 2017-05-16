# -*- coding: utf-8 -*-

import os

from cleo import CommandTester
from poet.console import Application
from poet.console.commands import UpdateCommand as BaseCommand
from poet.poet import Poet as BasePoet
from pip.req.req_install import InstallRequirement


class Poet(BasePoet):

    pass


class UpdateCommand(BaseCommand):

    @property
    def poet_file(self):
        return os.path.join(os.path.dirname(__file__), '..', 'fixtures', 'poetry.toml')

    @property
    def poet(self):
        return Poet(self.poet_file)

    def pip(self):
        return 'pip'


def test_update_only_update(mocker):
    sub = mocker.patch('subprocess.check_output')
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    get_hashes = mocker.patch('piptools.resolver.Resolver.resolve_hashes')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    reverse_dependencies.return_value = {}
    write_lock = mocker.patch('poet.installer.Installer._write_lock')
    pendulum_req = InstallRequirement.from_line('pendulum==1.3.0')
    pytest_req = InstallRequirement.from_line('pytest==3.5.0')
    resolve.return_value = [
        pendulum_req,
        pytest_req
    ]
    get_hashes.return_value = {
        pendulum_req: set([
            "sha256:a97e3ed9557ac0c5c3742f21fa4d852d7a050dd9b1b517e993aebef2dd2eea52",
            "sha256:641140a05f959b37a177866e263f6f53a53b711fae6355336ee832ec1a59da8a"
        ]),
        pytest_req: set([
            "sha256:66f332ae62593b874a648b10a8cb106bfdacd2c6288ed7dec3713c3a808a6017",
            "sha256:b70696ebd1a5e6b627e7e3ac1365a4bc60aaf3495e843c1e70448966c5224cab"
        ])
    }
    app = Application()
    app.add(UpdateCommand())

    command = app.find('update')
    command_tester = CommandTester(command)
    command_tester.execute([('command', command.name), ('--no-progress', True)])

    assert sub.call_count == 2
    write_lock.assert_called_once()

    output = command_tester.get_display()
    expected = """
Updating dependencies

Resolving dependencies
Package operations: 0 installs, 2 updates and 0 uninstalls
 - Updating pendulum (1.2.0 -> 1.3.0)
 - Updating pytest (3.0.7 -> 3.5.0)
"""

    assert output == expected


def test_update_specific_packages(mocker):
    sub = mocker.patch('subprocess.check_output')
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    get_hashes = mocker.patch('piptools.resolver.Resolver.resolve_hashes')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    reverse_dependencies.return_value = {}
    write_lock = mocker.patch('poet.installer.Installer._write_lock')
    pendulum_req = InstallRequirement.from_line('pendulum==1.3.0')
    pytest_req = InstallRequirement.from_line('pytest==3.5.0')
    resolve.return_value = [
        pendulum_req,
        pytest_req
    ]
    get_hashes.return_value = {
        pendulum_req: set([
            "sha256:a97e3ed9557ac0c5c3742f21fa4d852d7a050dd9b1b517e993aebef2dd2eea52",
            "sha256:641140a05f959b37a177866e263f6f53a53b711fae6355336ee832ec1a59da8a"
        ]),
        pytest_req: set([
            "sha256:66f332ae62593b874a648b10a8cb106bfdacd2c6288ed7dec3713c3a808a6017",
            "sha256:b70696ebd1a5e6b627e7e3ac1365a4bc60aaf3495e843c1e70448966c5224cab"
        ])
    }
    app = Application()
    app.add(UpdateCommand())

    command = app.find('update')
    command_tester = CommandTester(command)
    command_tester.execute([('command', command.name), ('packages', ['pendulum']), ('--no-progress', True)])

    assert sub.call_count == 1
    write_lock.assert_called_once()

    output = command_tester.get_display()
    expected = """
Updating dependencies

Resolving dependencies
Package operations: 0 installs, 1 update and 0 uninstalls
 - Updating pendulum (1.2.0 -> 1.3.0)
"""

    assert output == expected


def test_update_with_new_packages(mocker):
    sub = mocker.patch('subprocess.check_output')
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    get_hashes = mocker.patch('piptools.resolver.Resolver.resolve_hashes')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    reverse_dependencies.return_value = {'requests': set()}
    write_lock = mocker.patch('poet.installer.Installer._write_lock')
    pendulum_req = InstallRequirement.from_line('pendulum==1.3.0')
    pytest_req = InstallRequirement.from_line('pytest==3.5.0')
    requests_req = InstallRequirement.from_line('requests==2.13.0')
    resolve.return_value = [
        pendulum_req,
        pytest_req,
        requests_req
    ]
    get_hashes.return_value = {
        pendulum_req: set([
            "sha256:a97e3ed9557ac0c5c3742f21fa4d852d7a050dd9b1b517e993aebef2dd2eea52",
            "sha256:641140a05f959b37a177866e263f6f53a53b711fae6355336ee832ec1a59da8a"
        ]),
        pytest_req: set([
            "sha256:66f332ae62593b874a648b10a8cb106bfdacd2c6288ed7dec3713c3a808a6017",
            "sha256:b70696ebd1a5e6b627e7e3ac1365a4bc60aaf3495e843c1e70448966c5224cab"
        ]),
        requests_req: set([
            "sha256:5722cd09762faa01276230270ff16af7acf7c5c45d623868d9ba116f15791ce8",
            "sha256:1a720e8862a41aa22e339373b526f508ef0c8988baf48b84d3fc891a8e237efb"
        ])
    }
    app = Application()
    app.add(UpdateCommand())

    command = app.find('update')
    command_tester = CommandTester(command)
    command_tester.execute([('command', command.name), ('--no-progress', True)])

    assert sub.call_count == 3
    write_lock.assert_called_once()

    output = command_tester.get_display()
    expected = """
Updating dependencies

Resolving dependencies
Package operations: 1 install, 2 updates and 0 uninstalls
 - Updating pendulum (1.2.0 -> 1.3.0)
 - Updating pytest (3.0.7 -> 3.5.0)
 - Installing requests (2.13.0)
"""

    assert output == expected


def test_update_with_no_updates(mocker):
    sub = mocker.patch('subprocess.check_output')
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    get_hashes = mocker.patch('piptools.resolver.Resolver.resolve_hashes')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    reverse_dependencies.return_value = {}
    write_lock = mocker.patch('poet.installer.Installer._write_lock')
    pendulum_req = InstallRequirement.from_line('pendulum==1.2.0')
    pytest_req = InstallRequirement.from_line('pytest==3.0.7')
    resolve.return_value = [
        pendulum_req,
        pytest_req
    ]
    get_hashes.return_value = {
        pendulum_req: set([
            "sha256:a97e3ed9557ac0c5c3742f21fa4d852d7a050dd9b1b517e993aebef2dd2eea52",
            "sha256:641140a05f959b37a177866e263f6f53a53b711fae6355336ee832ec1a59da8a"
        ]),
        pytest_req: set([
            "sha256:66f332ae62593b874a648b10a8cb106bfdacd2c6288ed7dec3713c3a808a6017",
            "sha256:b70696ebd1a5e6b627e7e3ac1365a4bc60aaf3495e843c1e70448966c5224cab"
        ])
    }
    app = Application()
    app.add(UpdateCommand())

    command = app.find('update')
    command_tester = CommandTester(command)
    command_tester.execute([('command', command.name), ('--no-progress', True)])

    assert sub.call_count == 0
    assert write_lock.call_count == 0

    output = command_tester.get_display()
    expected = """
Updating dependencies

Resolving dependencies
Dependencies already up-to-date!
"""

    assert output == expected
