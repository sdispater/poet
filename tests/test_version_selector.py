# -*- coding: utf-8 -*-

import httpretty
from poet.repositories.pypi_repository import PyPiRepository
from poet.version_selector import VersionSelector
from poet.package import Package


RESPONSE = """<?xml version='1.0'?>
<methodResponse>
    <params>
        <param>
            <value>
                <array>
                    <data>
                        <value><string>1.2.0</string></value>
                        <value><string>1.1.1</string></value>
                        <value><string>1.3.0b2</string></value>
                        <value><string>1.1.0</string></value>
                        <value><string>1.2.1b0</string></value>
                        <value><string>1.0.2</string></value>
                        <value><string>1.0.1</string></value>
                        <value><string>1.0.0</string></value>
                    </data>
                </array>
            </value>
        </param>
    </params>
</methodResponse>
"""


@httpretty.activate
def test_find_best_candidate_stable():
    httpretty.register_uri(
        httpretty.POST, 'https://pypi.python.org/pypi',
        body=RESPONSE,
        content_type='text/xml'
    )

    selector = VersionSelector(PyPiRepository())
    package = selector.find_best_candidate('pendulum')

    assert package.name == 'pendulum'
    assert package.pretty_version == '1.2.0'


@httpretty.activate
def test_find_best_candidate_constraint():
    httpretty.register_uri(
        httpretty.POST, 'https://pypi.python.org/pypi',
        body=RESPONSE,
        content_type='text/xml'
    )

    selector = VersionSelector(PyPiRepository())
    package = selector.find_best_candidate('pendulum', '~1.1')

    assert package.name == 'pendulum'
    assert package.pretty_version == '1.1.1'


@httpretty.activate
def test_find_best_candidate_dev():
    httpretty.register_uri(
        httpretty.POST, 'https://pypi.python.org/pypi',
        body=RESPONSE,
        content_type='text/xml'
    )

    selector = VersionSelector(PyPiRepository())
    package = selector.find_best_candidate('pendulum', preferred_stability='dev')

    assert package.name == 'pendulum'
    assert package.pretty_version == '1.3.0b2'


@httpretty.activate
def test_find_best_candidate_constraint_dev():
    httpretty.register_uri(
        httpretty.POST, 'https://pypi.python.org/pypi',
        body=RESPONSE,
        content_type='text/xml'
    )

    selector = VersionSelector(PyPiRepository())
    package = selector.find_best_candidate('pendulum', '~1.2.0,<1.3.0', preferred_stability='dev')

    assert package.name == 'pendulum'
    assert package.pretty_version == '1.2.1b0'


@httpretty.activate
def test_find_best_candidate_no_candidate():
    httpretty.register_uri(
        httpretty.POST, 'https://pypi.python.org/pypi',
        body=RESPONSE,
        content_type='text/xml'
    )

    selector = VersionSelector(PyPiRepository())
    package = selector.find_best_candidate('pendulum', '^1.4', preferred_stability='dev')

    assert not package


def test_find_recommended_require_version():
    selector = VersionSelector(PyPiRepository())
    package = Package('pendulum', '1.2.3')

    assert '^1.2' == selector.find_recommended_require_version(package)
