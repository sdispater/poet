# -*- coding: utf-8 -*-

import os
import sys
import glob
import distutils
import re

from cleo import Command as BaseCommand
from semantic_version import Version

from ...poet import Poet
from ...utils.helpers import call


class Command(BaseCommand):
    
    def __init__(self):
        super(Command, self).__init__()

        self._poet = None
        self._virtual_env = None

        self._python_version = None

    @property
    def poet_file(self):
        return os.path.join(os.getcwd(), 'poetry.toml')

    @property
    def poet(self):
        """
        Return the Poet instance.

        :rtype: poet.poet.Poet
        """
        if self._poet is None:
            self._poet = Poet(self.poet_file)

        return self._poet

    @property
    def lock_file(self):
        return self.poet.lock_file

    @property
    def virtual_env(self):
        return self._virtual_env

    def has_lock(self):
        return os.path.exists(self.lock_file)

    def execute(self, i, o):
        """
        Executes the command.
        """
        # Adding warning style
        self.set_style('warning', 'black', 'yellow')
        self.set_style('question', 'blue')

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
            self._virtual_env = os.path.join(os.environ['VIRTUAL_ENV'], 'Lib', 'site-packages')
        else:
            lib = os.path.join(
                os.environ['VIRTUAL_ENV'], 'lib'
            )

            python = glob.glob(os.path.join(lib, 'python*'))[0].replace(lib + '/', '')

            self._virtual_env = os.path.join(
                lib,
                python,
                'site-packages'
            )

    def pip(self):
        if not self._virtual_env:
            return distutils.spawn.find_executable('pip')

        return os.path.realpath(
            os.path.join(self._virtual_env, '..', '..', '..', 'bin', 'pip')
        )

    def python(self):
        if not self._virtual_env:
            return distutils.spawn.find_executable('python')

        return os.path.realpath(
            os.path.join(self._virtual_env, '..', '..', '..', 'bin', 'python')
        )

    @property
    def python_version(self):
        if self._python_version is None:
            output = call([self.python(), '-V'])

            m = re.match('Python ([\d.]+)', output)
            if not m:
                raise RuntimeError('Unable to get the Python version.')

            self._python_version = Version.coerce(m.group(1))

        return self._python_version
