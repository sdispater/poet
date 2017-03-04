# -*- coding: utf-8 -*-

import os

from ....build import Builder

from ..command import Command


TEMPLATE="""from setuptools import setup

kwargs = {}

setup(**kwargs)
"""


class MakeSetupCommand(Command):
    """
    Renders a setup.py for testing purposes.

    make:setup
    """

    def handle(self):
        poet = self.poet
        builder = Builder()

        setup = builder._setup(poet)

        builder._write_setup(setup, os.path.join(os.path.dirname(self.poet_file), 'setup.py'))
