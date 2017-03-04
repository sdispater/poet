# -*- coding: utf-8 -*-

import os
import shutil

from .command import Command


class PackageCommand(Command):
    """
    Builds the package.

    package
        { --c|clean : MAke a clean package. }
    """

    def handle(self):
        poet = self.poet

        if self.option('clean'):
            egg_info = os.path.join(poet.base_dir, '{}.egg-info'.format(poet.name))

            if os.path.exists(egg_info):
                shutil.rmtree(egg_info)

        fmt = 'tar.gz'

        self.line('')
        self.line('<info>Building <comment>{}.{}</></>'.format(poet.name, fmt))

        poet.build()

        self.line('<info><comment>{}.{}</> built!</>'.format(poet.name, fmt))
        self.line('')
