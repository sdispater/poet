# -*- coding: utf-8 -*-

import os
import sys

from cleo import Command as BaseCommand, InputOption

from ...repositories import PyPiRepository
from ...sonnet import Sonnet


class Command(BaseCommand):
    
    def __init__(self):
        super(Command, self).__init__()

        self._sonnet = None
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
        if self._sonnet is None:
            self._sonnet = Sonnet(self.sonnet_file)

        return self._sonnet

    @property
    def lock_file(self):
        return self.sonnet.lock_file

    def has_lock(self):
        return os.path.exists(self.lock_file)

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

        self.init_virtualenv()

        return super(Command, self).execute(i, o)

    def init_virtualenv(self):
        if 'VIRTUAL_ENV' not in os.environ:
            # Not in a virtualenv
            return

        # venv detection:
        # stdlib venv may symlink sys.executable, so we can't use realpath.
        # but others can symlink *to* the venv Python, so we can't just use sys.executable.
        # So we just check every item in the symlink tree (generally <= 3)
        p = os.path.normcase(sys.executable)
        paths = [p]
        while os.path.islink(p):
            p = os.path.normcase(os.path.join(os.path.dirname(p), os.readlink(p)))
            paths.append(p)

        p_venv = os.path.normcase(os.environ['VIRTUAL_ENV'])
        if any(p.startswith(p_venv) for p in paths):
            # Running properly in the virtualenv, don't need to do anything
            return

        if self.output.is_verbose():
            self.line('Using virtualenv <comment>{}</>'.format(os.environ['VIRTUAL_ENV']))

        if sys.platform == "win32":
            virtual_env = os.path.join(os.environ['VIRTUAL_ENV'], 'Lib', 'site-packages')
        else:
            virtual_env = os.path.join(
                os.environ['VIRTUAL_ENV'], 'lib',
                'python{}.{}'.format(*sys.version_info[:2]),
                'site-packages'
            )

        import site
        sys.path.insert(0, virtual_env)

        site.addsitedir(virtual_env)
