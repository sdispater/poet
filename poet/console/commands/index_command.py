# -*- coding: utf-8 -*-

from cleo import InputOption

from ...repositories import PyPiRepository

from .command import Command


class IndexCommand(Command):

    def __init__(self):
        super(IndexCommand, self).__init__()

        self._repository = PyPiRepository()

    def configure(self):
        super(IndexCommand, self).configure()

        # Adding --i|index option
        self.add_option(
            'index', 'i',
            InputOption.VALUE_REQUIRED,
            'The index to use'
        )

    def execute(self, i, o):
        super(IndexCommand, self).execute(i, o)

        index = self.option('index')

        if index:
            self._repository = PyPiRepository(index)
