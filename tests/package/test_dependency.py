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


def test_accepts_prereleases():
    dep = Dependency('foo', '1.2.3')

    assert not dep.accepts_prereleases()

    dep = Dependency('foo', '1.2.3-beta')

    assert dep.accepts_prereleases()

    dep = Dependency('foo', '1.2.3-rc.2')

    assert dep.accepts_prereleases()

    dep = Dependency('foo', '^1.2.3-rc.2')

    assert dep.accepts_prereleases()


def test_basic_dependency():
    dep = Dependency('foo', '1.2.3')

    assert 'foo' == dep.name
    assert '==1.2.3' == dep.normalized_constraint
    assert 'foo==1.2.3' == dep.normalized_name
    assert not dep.optional
    assert '1.2.3' == dep.constraint
    assert '1.2.3' == dep.pretty_constraint
    assert not dep.is_vcs_dependency()
    assert not dep.accepts_prereleases()
    assert ['*'] == [str(dep.python[0])]


def test_vcs_dependency():
    constraint = {
        'git': 'https://github.com/sdispater/poet.git',
        'branch': 'master'
    }
    dep = Dependency('foo', constraint)

    assert 'foo' == dep.name
    assert '' == dep.normalized_constraint
    assert 'foo' == dep.normalized_name
    assert not dep.optional
    assert constraint == dep.constraint
    assert 'branch master' == dep.pretty_constraint
    assert dep.is_vcs_dependency()
    assert not dep.accepts_prereleases()
    assert ['*'] == [str(dep.python[0])]


def test_optional_dependency():
    constraint = {
        'version': '^1.2.3',
        'optional': True
    }

    dep = Dependency('foo', constraint)

    assert 'foo' == dep.name
    assert '>=1.2.3,<2.0.0' == dep.normalized_constraint
    assert 'foo>=1.2.3,<2.0.0' == dep.normalized_name
    assert dep.optional
    assert constraint == dep.constraint
    assert constraint == dep.pretty_constraint
    assert not dep.is_vcs_dependency()
    assert not dep.accepts_prereleases()
    assert ['*'] == [str(dep.python[0])]


def test_python_restricted_dependency():
    constraint = {
        'version': '^1.2.3',
        'python': '~2.7'
    }

    dep = Dependency('foo', constraint)

    assert 'foo' == dep.name
    assert '>=1.2.3,<2.0.0' == dep.normalized_constraint
    assert 'foo>=1.2.3,<2.0.0' == dep.normalized_name
    assert not dep.optional
    assert constraint == dep.constraint
    assert constraint == dep.pretty_constraint
    assert not dep.is_vcs_dependency()
    assert not dep.accepts_prereleases()
    assert ['~2.7'] == [str(dep.python[0])]
