# -*- coding: utf-8 -*-

from cleo import Application as BaseApplication

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
from .commands.make import MakeSetupCommand, MakeRequirementsCommand


class Application(BaseApplication):
    """
    The console application that handles the commands.
    """

    def get_default_commands(self):
        default_commands = super(Application, self).get_default_commands()

        return default_commands + [
            AboutCommand(),
            CheckCommand(),
            InitCommand(),
            InstallCommand(),
            LockCommand(),
            MakeRequirementsCommand(),
            MakeSetupCommand(),
            PackageCommand(),
            PublishCommand(),
            RequireCommand(),
            SearchCommand(),
            UpdateCommand()
        ]


if __name__ == '__main__':
    Application().run()
