# -*- coding: utf-8 -*-

import pytest
from pip.req.req_install import InstallRequirement

from poet.installer import Installer
from poet.repositories import PyPiRepository
from poet.package.pip_dependency import PipDependency

pendulum_req = InstallRequirement.from_line('pendulum==1.2.1')
orator_req = InstallRequirement.from_line('orator==0.9.7')
requests_req = InstallRequirement.from_line('requests==2.14.0')
pytest_req = InstallRequirement.from_line('pytest==3.0.7')

pendulum_hashes = [
    'sha256:a97e3ed9557ac0c5c3742f21fa4d852d7a050dd9b1b517e993aebef2dd2eea52',
    'sha256:641140a05f959b37a177866e263f6f53a53b711fae6355336ee832ec1a59da8a'
]
orator_hashes = [
    'sha256:a4d11b8123d00e947fac88508292b9e148da884fc64b884d9da3897a35fa2ab0',
    'sha256:ec36940a8eec0a2ebc66a257a746428f7b4acce24cc000b3cda4805f259a8cd2'
]
requests_hashes = [
    'sha256:66f332ae62593b874a648b10a8cb106bfdacd2c6288ed7dec3713c3a808a6017',
    'sha256:b70696ebd1a5e6b627e7e3ac1365a4bc60aaf3495e843c1e70448966c5224cab'
]


def test_update_specific_packages(mocker, command):
    installer = Installer(command, PyPiRepository())
    current_deps = command.poet.lock.pip_dependencies + command.poet.lock.pip_dev_dependencies

    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    resolve_hashes = mocker.patch('piptools.resolver.Resolver.resolve_hashes')
    resolve.side_effect = [
        [pendulum_req, orator_req, requests_req],
        [pendulum_req, orator_req, requests_req, pytest_req],
    ]
    reverse_dependencies.return_value = {}
    resolve_hashes.return_value = {
        pendulum_req: set(pendulum_hashes),
        requests_req: set(requests_hashes),
        orator_req: set(orator_hashes),
        pytest_req: set(orator_hashes),
    }

    perform_update_actions = mocker.patch('poet.installer.Installer._perform_update_actions')
    write_lock = mocker.patch('poet.installer.Installer._write_lock')

    installer.update(packages=['orator'])

    perform_update_actions.assert_called_with([
        ('install', None, PipDependency('orator', '==0.9.7')),
        ('update', PipDependency('pendulum', '==1.2.0'), PipDependency('pendulum', '==1.2.1')),
        ('update', PipDependency('requests', '==2.13.0'), PipDependency('requests', '==2.14.0')),
    ])
    write_lock.assert_called_with([
        {
            'name': 'orator',
            'version': '0.9.7',
            'checksum': list(sorted(orator_hashes)),
            'category': 'main',
            'optional': False,
            'python': ['*']
        },
        {
            'name': 'pendulum',
            'version': '1.2.1',
            'checksum': list(sorted(pendulum_hashes)),
            'category': 'main',
            'optional': False,
            'python': ['*']
        },
        {
            'name': 'pytest',
            'version': '3.0.7',
            'checksum': list(sorted(orator_hashes)),
            'category': 'dev',
            'optional': False,
            'python': ['*']
        },
        {
            'name': 'requests',
            'version': '2.14.0',
            'checksum': list(sorted(requests_hashes)),
            'category': 'main',
            'optional': False,
            'python': ['*']
        },
    ], {})
