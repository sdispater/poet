# -*- coding: utf-8 -*-

from poet.package.dependency import Dependency


def test_normalized_caret():
    dep = Dependency('foo', '^1')

    assert '>=1.0.0,<2.0.0' == dep.normalized_constraint

    dep = Dependency('foo', '^1.2')

    assert '>=1.2.0,<2.0.0' == dep.normalized_constraint

    dep = Dependency('foo', '^1.2.3')

    assert '>=1.2.3,<2.0.0' == dep.normalized_constraint

    dep = Dependency('foo', '^0')

    assert '>=0.0.0,<1.0.0' == dep.normalized_constraint

    dep = Dependency('foo', '^0.0')

    assert '>=0.0.0,<0.1.0' == dep.normalized_constraint

    dep = Dependency('foo', '^0.0.3')

    assert '>=0.0.3,<0.0.4' == dep.normalized_constraint


def test_normalized_tilde():
    dep = Dependency('foo', '~1')

    assert '>=1.0.0,<2.0.0' == dep.normalized_constraint

    dep = Dependency('foo', '~1.2')

    assert '>=1.2.0,<1.3.0' == dep.normalized_constraint

    dep = Dependency('foo', '~1.2.3')

    assert '>=1.2.3,<1.3.0' == dep.normalized_constraint


def test_normalized_complex():
    dep = Dependency('foo', '~2.7,!=2.7.6,>=2.7.5')

    assert '>=2.7.0,<2.8.0,!=2.7.6,>=2.7.5' == dep.normalized_constraint


def test_normalized_name():
    dep = Dependency('foo', '~1.2')

    assert 'foo>=1.2.0,<1.3.0' == dep.normalized_name
