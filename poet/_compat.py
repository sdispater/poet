# -*- coding: utf-8 -*-

import sys

PY2 = sys.version_info[0] == 2
PY3K = sys.version_info[0] >= 3
PY33 = sys.version_info >= (3, 3)
PY35 = sys.version_info >= (3, 5)


if PY2:
    reload = reload
elif PY35:
    import importlib

    reload = importlib.reload
else:
    import imp

    reload = imp.reload
