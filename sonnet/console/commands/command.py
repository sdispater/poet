# -*- coding: utf-8 -*-

import os

from cleo import Command as BaseCommand, InputOption

from ...repositories import PyPiRepository
from ...sonnet import Sonnet


class Command(BaseCommand):
    
    def __init__(self):
        super(Command, self).__init__()

        self._repository = PyPiRepository()

    @property
    def sonnet_file(self):
        return os.path.join(os.getcwd(), 'sonnet.toml')

    @property
    def sonnet(self):
        """
        Return the Sonnet instance.

        :rtype: sonnet.sonnet.Sonnet
        """
        return Sonnet(self.sonnet_file)

    def configure(self):
        super(Command, self).configure()

        # Adding --i|index option
        self.add_option(
            'index', 'i',
            InputOption.VALUE_REQUIRED,
            'The index to use'
        )

    def execute(self, i, o):
        """
        Executes the command.
        """
        index = self.option('index')

        if index:
            self._repository = PyPiRepository(index)

        return super(Command, self).execute(i, o)
