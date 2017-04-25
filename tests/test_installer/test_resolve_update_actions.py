# -*- coding: utf-8 -*-

from poet.installer import Installer
from poet.repositories import PyPiRepository
from poet.package import PipDependency

foo_dependency_123 = PipDependency('foo', '1.2.3')
foo_dependency_133 = PipDependency('foo', '1.3.3')
bar_dependency_321 = PipDependency('bar', '3.2.1')
baz_dependency_233 = PipDependency('baz', '2.3.3')


def test_resolve_update_actions_up_to_date(command):
    installer = Installer(command, PyPiRepository())
    current_deps = [
        PipDependency('foo', '1.2.3'),
        PipDependency('bar', '3.2.1')
    ]
    deps = [
        PipDependency('foo', '1.2.3'),
        PipDependency('bar', '3.2.1')
    ]

    actions = installer._resolve_update_actions(
        deps, current_deps
    )

    assert [] == actions


def test_resolve_update_actions_upgrade(command):
    installer = Installer(command, PyPiRepository())
    current_deps = [
        foo_dependency_123,
        bar_dependency_321
    ]
    deps = [
        foo_dependency_133,
        PipDependency('bar', '3.2.1')
    ]

    actions = installer._resolve_update_actions(
        deps, current_deps
    )

    expected = [
        ('update', foo_dependency_123, foo_dependency_133)
    ]
    assert expected == actions


def test_resolve_update_actions_install(command):
    installer = Installer(command, PyPiRepository())
    current_deps = [
        foo_dependency_123
    ]
    deps = [
        foo_dependency_123,
        bar_dependency_321
    ]

    actions = installer._resolve_update_actions(
        deps, current_deps
    )

    expected = [
        ('install', None, bar_dependency_321)
    ]
    assert expected == actions


def test_resolve_update_actions_remove(command):
    installer = Installer(command, PyPiRepository())
    current_deps = [
        foo_dependency_123,
        bar_dependency_321
    ]
    deps = [
        foo_dependency_123
    ]

    actions = installer._resolve_update_actions(
        deps, current_deps
    )

    expected = [
        ('remove', None, bar_dependency_321)
    ]
    assert expected == actions


def test_resolve_update_actions_all(command):
    installer = Installer(command, PyPiRepository())
    current_deps = [
        foo_dependency_123,
        bar_dependency_321
    ]
    deps = [
        foo_dependency_133,
        baz_dependency_233
    ]

    actions = installer._resolve_update_actions(
        deps, current_deps
    )

    expected = [
        ('update', foo_dependency_123, foo_dependency_133),
        ('install', None, baz_dependency_233),
        ('remove', None, bar_dependency_321)
    ]
    assert expected == actions
