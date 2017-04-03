# -*- coding: utf-8 -*-

from poet.installer import Installer
from poet.console.commands.install import InstallCommand
from poet.repositories import PyPiRepository


def test_install():
    installer = Installer(InstallCommand(), PyPiRepository())

    installer.install()
