# -*- coding: utf-8 -*-

import os

from twine.commands.upload import upload
from twine.commands.register import register
from requests.exceptions import HTTPError

from .command import Command


class PublishCommand(Command):
    """
    Publish the package to the remote repository.

    publish
        {--r|repository : The repository to register the package to}
    """

    def handle(self):
        # Checking if package exists
        dist = os.path.join(self.poet.base_dir, 'dist')
        package = os.path.join(dist, '{}-{}.tar.gz'.format(self.poet.name, self.poet.version))

        if not os.path.exists(package):
            self.info('No package found. Building it.')
            self.line('')
            self.call('package')
            self.line('')
            self.info('Package built.')
        else:
            self.info('Package found. Proceeding with publishing.')

        self.line('')
        self.line('Publishing <info>{}</> (<comment>{}</>)'.format(self.poet.name, self.poet.version))

        try:
            self._upload(dist, package)
        except HTTPError as e:
            if e.response.status_code != 403:
                raise

            # It may be the first time we publish the package
            # We'll try to register it and go from there
            try:
                self._register(package)
            except HTTPError:
                raise

            self._upload(dist, package)

    def _upload(self, dist, package):
        upload(
            [os.path.join(dist, '{}-{}*'.format(self.poet.name, self.poet.version))],
            self.option('repository') or 'pypi',
            False,
            None,
            None,
            None,
            None,
            None,
            '~/.pypirc',
            False,
            None,
            None,
            None
        )

    def _register(self, package):
        register(
            package,
            self.option('repository') or 'pypi',
            None, None, None,
            '~/.pypirc',
            None, None, None
        )
