# -*- coding: utf-8 -*-

from cleo import Application as BaseApplication

from ..version import VERSION
from .commands import (
    AboutCommand,
    CheckCommand,
    InitCommand,
    InstallCommand,
    LockCommand,
    PackageCommand,
    PublishCommand,
    RequireCommand,
    SearchCommand,
    UpdateCommand
)
from .commands.make import MakeSetupCommand


class Application(BaseApplication):
    """
    The console application that handles the commands.
    """

    def __init__(self):
        super(Application, self).__init__('Poet', VERSION)

    def get_default_commands(self):
        default_commands = super(Application, self).get_default_commands()

        return default_commands + [
            AboutCommand(),
            CheckCommand(),
            InitCommand(),
            InstallCommand(),
            LockCommand(),
            MakeSetupCommand(),
            PackageCommand(),
            PublishCommand(),
            RequireCommand(),
            SearchCommand(),
            UpdateCommand()
        ]
