# -*- coding: utf-8 -*-

from ...repositories import PyPiRepository
from .index_command import IndexCommand


class SearchCommand(IndexCommand):
    """
    Search for packages.

    search
        {tokens* : The tokens to search for.}
        {--N|only-name : Search only in name.}
    """

    help = """The search command searches for packages by its name
<info>poet search requests pendulum</info>
"""

    def handle(self):
        flags = PyPiRepository.SEARCH_FULLTEXT
        if self.option('only-name'):
            flags = PyPiRepository.SEARCH_NAME

        results = self._repository.search(self.argument('tokens'), flags)

        for result in results:
            self.line('')
            name = '<info>{}</>'.format(
                result['name']
            )

            if 'version' in result:
                name += ' (<comment>{}</>)'.format(result['version'])

            self.line(name)

            if 'description' in result:
                self.line(
                    ' {}'.format(result['description'])
                )
