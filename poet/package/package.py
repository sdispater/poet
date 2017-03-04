# -*- coding: utf-8 -*-

import re

from ..version_parser import VersionParser, Version


class Package(object):

    def __init__(self, name, version):
        self._name = name
        self._version = Version.coerce(version) if not isinstance(version, Version) else version
        self._pretty_version = str(version)

        self._stability = VersionParser.parse_stability(version)
        self._dev = self._stability == 'dev'
        self._dependencies = []

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def pretty_version(self):
        return self._pretty_version

    @property
    def stability(self):
        return self._stability

    @property
    def dependencies(self):
        return self._dependencies

    @classmethod
    def check_name(cls, name):
        m = re.match('[a-z0-9\-]+/[a-z0-9\-]+', name)
        if m is None:
            return False

        return True

    def is_dev(self):
        return self._dev
