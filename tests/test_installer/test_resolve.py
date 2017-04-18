# -*- coding: utf-8 -*-

from pip.req.req_install import InstallRequirement

from poet.installer import Installer
from poet.repositories import PyPiRepository
from poet.package.pip_dependency import PipDependency

pendulum_req = InstallRequirement.from_line('pendulum==1.2.0')
pytzdata_req = InstallRequirement.from_line('pytzdata==2017.2')
requests_req = InstallRequirement.from_line('requests==2.13.0')

pendulum_hashes = [
    'sha256:a97e3ed9557ac0c5c3742f21fa4d852d7a050dd9b1b517e993aebef2dd2eea52',
    'sha256:641140a05f959b37a177866e263f6f53a53b711fae6355336ee832ec1a59da8a'
]
pytzdata_hashes = [
    'sha256:a4d11b8123d00e947fac88508292b9e148da884fc64b884d9da3897a35fa2ab0',
    'sha256:ec36940a8eec0a2ebc66a257a746428f7b4acce24cc000b3cda4805f259a8cd2'
]
requests_hashes = [
    'sha256:66f332ae62593b874a648b10a8cb106bfdacd2c6288ed7dec3713c3a808a6017',
    'sha256:b70696ebd1a5e6b627e7e3ac1365a4bc60aaf3495e843c1e70448966c5224cab'
]


def test_resolve(mocker, command):
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    resolve_hashes = mocker.patch('piptools.resolver.Resolver.resolve_hashes')
    resolve.return_value = [
        pendulum_req,
        pytzdata_req,
        requests_req,
    ]
    reverse_dependencies.return_value = {
        'pytzdata': set(['pendulum'])
    }
    resolve_hashes.return_value = {
        pendulum_req: set(pendulum_hashes),
        requests_req: set(requests_hashes),
        pytzdata_req: set(pytzdata_hashes),
    }

    installer = Installer(command, PyPiRepository())

    packages = installer._resolve([
        PipDependency('pendulum', '^1.2'),
        PipDependency('requests', '^2.13')
    ])

    pendulum = packages[0]
    pytzdata = packages[1]
    requests = packages[2]

    # Name
    assert 'pendulum' == pendulum['name']
    assert 'pytzdata' == pytzdata['name']
    assert 'requests' == requests['name']

    # Version
    assert '1.2.0' == pendulum['version']
    assert '2017.2' == pytzdata['version']
    assert '2.13.0' == requests['version']

    # Version
    assert set(pendulum_hashes) == set(pendulum['checksum'])
    assert set(pytzdata_hashes) == set(pytzdata['checksum'])
    assert set(requests_hashes) == set(requests['checksum'])

    # Category
    assert 'main' == pendulum['category']
    assert 'main' == pytzdata['category']
    assert 'main' == requests['category']

    # Optional
    assert not pendulum['optional']
    assert not pytzdata['optional']
    assert not requests['optional']

    # Python
    assert ['*'] == pendulum['python']
    assert ['*'] == pytzdata['python']
    assert ['*'] == requests['python']


def test_resolve_specific_python(mocker, command):
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    resolve_hashes = mocker.patch('piptools.resolver.Resolver.resolve_hashes')
    resolve.return_value = [
        pendulum_req,
        pytzdata_req,
        requests_req,
    ]
    reverse_dependencies.return_value = {
        'pytzdata': set(['pendulum'])
    }
    resolve_hashes.return_value = {
        pendulum_req: set(pendulum_hashes),
        requests_req: set(requests_hashes),
        pytzdata_req: set(pytzdata_hashes),
    }

    installer = Installer(command, PyPiRepository())

    packages = installer._resolve([
        PipDependency('pendulum', '^1.2'),
        PipDependency('requests', {'version': '^2.13', 'python': '~2.7'})
    ])

    pendulum = packages[0]
    pytzdata = packages[1]
    requests = packages[2]

    # Name
    assert 'pendulum' == pendulum['name']
    assert 'pytzdata' == pytzdata['name']
    assert 'requests' == requests['name']

    # Version
    assert '1.2.0' == pendulum['version']
    assert '2017.2' == pytzdata['version']
    assert '2.13.0' == requests['version']

    # Version
    assert set(pendulum_hashes) == set(pendulum['checksum'])
    assert set(pytzdata_hashes) == set(pytzdata['checksum'])
    assert set(requests_hashes) == set(requests['checksum'])

    # Category
    assert 'main' == pendulum['category']
    assert 'main' == pytzdata['category']
    assert 'main' == requests['category']

    # Optional
    assert not pendulum['optional']
    assert not pytzdata['optional']
    assert not requests['optional']

    # Python
    assert ['*'] == pendulum['python']
    assert ['*'] == pytzdata['python']
    assert ['~2.7'] == requests['python']


def test_resolve_specific_python_parent(mocker, command):
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    resolve_hashes = mocker.patch('piptools.resolver.Resolver.resolve_hashes')
    resolve.return_value = [
        pendulum_req,
        pytzdata_req,
        requests_req,
    ]
    reverse_dependencies.return_value = {
        'pytzdata': set(['pendulum'])
    }
    resolve_hashes.return_value = {
        pendulum_req: set(pendulum_hashes),
        requests_req: set(requests_hashes),
        pytzdata_req: set(pytzdata_hashes),
    }

    installer = Installer(command, PyPiRepository())

    packages = installer._resolve([
        PipDependency('pendulum', {'version': '^1.2', 'python': '~2.7'}),
        PipDependency('requests', '^2.13')
    ])

    pendulum = packages[0]
    pytzdata = packages[1]
    requests = packages[2]

    # Name
    assert 'pendulum' == pendulum['name']
    assert 'pytzdata' == pytzdata['name']
    assert 'requests' == requests['name']

    # Version
    assert '1.2.0' == pendulum['version']
    assert '2017.2' == pytzdata['version']
    assert '2.13.0' == requests['version']

    # Version
    assert set(pendulum_hashes) == set(pendulum['checksum'])
    assert set(pytzdata_hashes) == set(pytzdata['checksum'])
    assert set(requests_hashes) == set(requests['checksum'])

    # Category
    assert 'main' == pendulum['category']
    assert 'main' == pytzdata['category']
    assert 'main' == requests['category']

    # Optional
    assert not pendulum['optional']
    assert not pytzdata['optional']
    assert not requests['optional']

    # Python
    assert ['~2.7'] == pendulum['python']
    assert ['~2.7'] == pytzdata['python']
    assert ['*'] == requests['python']


def test_resolve_specific_python_and_wildcard_multiple_parent(mocker, command):
    resolve = mocker.patch('piptools.resolver.Resolver.resolve')
    reverse_dependencies = mocker.patch('piptools.resolver.Resolver.reverse_dependencies')
    resolve_hashes = mocker.patch('piptools.resolver.Resolver.resolve_hashes')
    resolve.return_value = [
        pendulum_req,
        pytzdata_req,
        requests_req,
    ]
    reverse_dependencies.return_value = {
        'pytzdata': set(['pendulum', 'requests'])
    }
    resolve_hashes.return_value = {
        pendulum_req: set(pendulum_hashes),
        requests_req: set(requests_hashes),
        pytzdata_req: set(pytzdata_hashes),
    }

    installer = Installer(command, PyPiRepository())

    packages = installer._resolve([
        PipDependency('pendulum', {'version': '^1.2', 'python': '~2.7'}),
        PipDependency('requests', '^2.13')
    ])

    pendulum = packages[0]
    pytzdata = packages[1]
    requests = packages[2]

    # Name
    assert 'pendulum' == pendulum['name']
    assert 'pytzdata' == pytzdata['name']
    assert 'requests' == requests['name']

    # Version
    assert '1.2.0' == pendulum['version']
    assert '2017.2' == pytzdata['version']
    assert '2.13.0' == requests['version']

    # Version
    assert set(pendulum_hashes) == set(pendulum['checksum'])
    assert set(pytzdata_hashes) == set(pytzdata['checksum'])
    assert set(requests_hashes) == set(requests['checksum'])

    # Category
    assert 'main' == pendulum['category']
    assert 'main' == pytzdata['category']
    assert 'main' == requests['category']

    # Optional
    assert not pendulum['optional']
    assert not pytzdata['optional']
    assert not requests['optional']

    # Python
    assert ['~2.7'] == pendulum['python']
    assert ['*'] == pytzdata['python']
    assert ['*'] == requests['python']
