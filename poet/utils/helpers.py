# -*- coding: utf-8 -*-

import subprocess

from .._compat import decode, PY3K


def call(args):
    output = subprocess.check_output(args, stderr=subprocess.STDOUT)

    if PY3K:
        return decode(output)

    return output
