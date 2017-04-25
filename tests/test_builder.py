# -*- coding: utf-8 -*-

import os
import pytest

from poet.build import Builder
from poet.poet import Poet


def test_setup_basic(mocker):
    base_dir = os.path.join(
        os.path.dirname(__file__), '..', 'examples', 'basic'
    )

    getcwd = mocker.patch('os.getcwd')
    getcwd.return_value = base_dir
    path = os.path.join(
        base_dir, 'poetry.toml'
    )
    poet = Poet(path)
    builder = Builder()
    setup_kwargs = builder._setup(poet)

    assert 'basic-example' == setup_kwargs['name']
    assert '0.1.0' == setup_kwargs['version']
    assert 'Basic example' == setup_kwargs['description']

    long_description = """Basic Example
=============

This is a basic example of a Poet project.
"""
    assert long_description == setup_kwargs['long_description']
    assert setup_kwargs['include_package_data']
    assert 'setup.py' == setup_kwargs['script_name']

    assert 'Sébastien Eustace' == setup_kwargs['author']
    assert 'sebastien@eustace.io' == setup_kwargs['author_email']

    assert 'https://github.com/sdispater/poet' == setup_kwargs['url']
    assert 'MIT' == setup_kwargs['license']
    assert 'packaging poet' == setup_kwargs['keywords']

    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]

    assert classifiers == setup_kwargs['classifiers']
    assert {'console_scripts': []} == setup_kwargs['entry_points']
    assert ['requests>=2.13.0,<3.0.0'] == setup_kwargs['install_requires']
    assert ['pytest>=3.0.0,<4.0.0'] == setup_kwargs['tests_require']
    assert {} == setup_kwargs['extras_require']

    assert ['basic_example', 'basic_example.sub_package'] == setup_kwargs['packages']
    assert ['my_module'] == setup_kwargs['py_modules']


def test_setup_package_dir(mocker):
    base_dir = os.path.join(
        os.path.dirname(__file__), '..', 'examples', 'package_dir'
    )

    getcwd = mocker.patch('os.getcwd')
    getcwd.return_value = base_dir
    path = os.path.join(
        base_dir, 'poetry.toml'
    )
    poet = Poet(path)
    builder = Builder()
    setup_kwargs = builder._setup(poet)

    assert 'package-dir-example' == setup_kwargs['name']
    assert '0.1.0' == setup_kwargs['version']
    assert 'Package dir example' == setup_kwargs['description']

    long_description = """Package dir Example
===================

This is an example of a package dir Poet project.
"""
    assert long_description == setup_kwargs['long_description']
    assert ['my_package'] == setup_kwargs['packages']
    assert [] == setup_kwargs['py_modules']
    assert {'': 'src'} == setup_kwargs['package_dir']

