# -*- coding: utf-8 -*-

import os
import shutil

from .command import Command


class PackageCommand(Command):
    """
    Builds the package.

    package
        { --u|universal : Build universal wheel. }
        { --no-wheels : Build only the source package. }
        { --c|clean : Make a clean package. }
    """

    def handle(self):
        poet = self.poet

        if self.option('clean'):
            egg_info = os.path.join(poet.base_dir, '{}.egg-info'.format(poet.name))

            if os.path.exists(egg_info):
                shutil.rmtree(egg_info)

        fmt = 'tar.gz'

        self.line('')
        self.line('<info>Building <comment>{}-{}</></>'.format(poet.name, poet.version))

        poet.build(universal=self.option('universal'), no_wheels=self.option('no-wheels'))

        self.line('<info><comment>{}-{}</> built!</>'.format(poet.name, poet.version))
        self.line('')
