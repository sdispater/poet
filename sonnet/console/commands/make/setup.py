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
        sonnet = self.sonnet
        builder = Builder()

        setup = builder._setup(sonnet)

        builder._write_setup(setup, os.path.join(os.path.dirname(self.sonnet_file), 'setup.py'))
