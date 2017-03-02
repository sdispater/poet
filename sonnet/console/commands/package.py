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
        sonnet = self.sonnet

        if self.option('clean'):
            egg_info = os.path.join(sonnet.base_dir, '{}.egg-info'.format(sonnet.name))

            if os.path.exists(egg_info):
                shutil.rmtree(egg_info)

        fmt = 'tar.gz'

        self.line('')
        self.line('<info>Building <comment>{}.{}</></>'.format(sonnet.name, fmt))

        sonnet.build()

        self.line('<info><comment>{}.{}</> built!</>'.format(sonnet.name, fmt))
        self.line('')
