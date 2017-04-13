# -*- coding: utf-8 -*-

import pytest

from poet.console import Application


@pytest.fixture
def app():
    return Application()
