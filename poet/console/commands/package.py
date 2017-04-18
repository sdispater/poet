# -*- coding: utf-8 -*-

import os
import shutil

from ..._compat import Path
from .command import Command


class PackageCommand(Command):
    """
    Builds the package.

    package
        { --no-universal : Do not build a universal package. }
        { --no-wheels : Build only the source package. }
        { --c|clean : Make a clean package. }
    """

    def handle(self):
        poet = self.poet

        if self.option('clean'):
            egg_info = os.path.join(poet.base_dir, '{}.egg-info'.format(poet.name))

            if os.path.exists(egg_info):
                shutil.rmtree(egg_info)

        self.line('')
        self.line('Building <info>{}</> (<comment>{}</>)'.format(poet.name, poet.version))

        poet.build(
            universal=not self.option('no-universal'),
            no_wheels=self.option('no-wheels')
        )

        self.line('')

        dist = Path(self.poet_file).parent / 'dist'
        releases = dist.glob('{}-{}*'.format(self.poet.name, self.poet.normalized_version))
        for release in releases:
            self.line('  - Created <comment>{}</>'.format(release.name))

        self.line('')
