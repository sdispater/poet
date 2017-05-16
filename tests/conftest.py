# -*- coding: utf-8 -*-

import os
import pytest
import tempfile
import shutil

from cleo.inputs.list_input import ListInput
from cleo.outputs.console_output import ConsoleOutput
from cleo.styles import CleoStyle

from poet.console import Application
from poet.console.commands.command import Command


class DummyCommand(Command):
    """
    Dummy Command.
    
    dummy
    """

    def __init__(self):
        super(DummyCommand, self).__init__()

        self.input = ListInput([])
        self.output = CleoStyle(self.input, ConsoleOutput())


@pytest.fixture
def app():
    return Application()


@pytest.fixture
def command():
    return DummyCommand()


@pytest.fixture
def check_output(mocker):
    outputs = {
        ('python', '-V'): b'Python 3.6.0',
        ('pip', 'freeze'): """requests==2.13.0
-e -e git+git@github.com:sdispater/cleo.git@d54cb993b2342e95ae4fce817af8a841c43514ef#egg=cleo'
"""
    }
    patched = mocker.patch(
        'subprocess.check_output',
        side_effect=lambda cmd, *args, **kwargs: outputs.get(tuple(cmd), b'')
    )

    return patched


@pytest.fixture
def tmp_dir():
    dir_ = tempfile.mkdtemp(prefix='poet_')

    yield dir_

    shutil.rmtree(dir_)


@pytest.fixture
def tmp_file():
    fd, file_ = tempfile.mkstemp(prefix='poet_')
    os.close(fd)

    yield file_

    os.unlink(file_)
