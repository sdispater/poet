# -*- coding: utf-8 -*-

import pytest
import tempfile
import shutil

from poet.console import Application


@pytest.fixture
def app():
    return Application()


@pytest.fixture
def tmp_dir():
    dir_ = tempfile.mkdtemp(prefix='poet_')

    yield dir_

    shutil.rmtree(dir_)
