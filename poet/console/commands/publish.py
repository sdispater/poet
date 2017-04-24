# -*- coding: utf-8 -*-

import os

from twine.commands.upload import upload
from twine.commands.register import register
from requests.exceptions import HTTPError

from ...publisher import Publisher

from .command import Command


class PublishCommand(Command):
    """
    Publish the package to the remote repository.

    publish
        {--r|repository=pypi : The repository to register the package to}
    """

    def handle(self):
        # Checking if package exists
        package = os.path.join(self.poet.base_dir, 'dist', self.poet.archive)

        if not os.path.exists(package):
            self.info('No package found. Building it.')
            self.line('')
            self.call('package')
        else:
            self.info('Package found. Proceeding with publishing.')

        self.line('')
        self.line(
            'Publishing <info>{}</> (<comment>{}</>) to <fg=blue>{}</>'
            .format(self.poet.name, self.poet.version, self.option('repository'))
        )

        publisher = Publisher(
            self.output,
            self.option('repository')
        )

        self.line('')

        try:
            publisher.upload(self.poet)
        except HTTPError as e:
            if (e.response.status_code not in (403, 400)
                or e.response.status_code == 400 and 'was ever registered' not in e.response.text):
                raise

            # It may be the first time we publish the package
            # We'll try to register it and go from there
            try:
                publisher.register(self.poet)
            except HTTPError:
                raise

            publisher.upload(self.poet)
