# -*- coding: utf-8 -*-

import re

from semantic_version import Spec, Version


class VersionParser(object):

    _constraints = {}

    def parse_constraints(self, constraints):
        if not isinstance(constraints, list):
            constraints = constraints.replace(', ', ',')
        else:
            constraints = ','.join(constraints)

        if constraints not in self.__class__._constraints:
            specs = Spec(constraints)

            self.__class__._constraints[constraints] = specs

        return self.__class__._constraints[constraints]

    @classmethod
    def parse_stability(cls, version):
        if not isinstance(version, Version):
            version = Version.coerce(version)

        if version.prerelease:
            return 'dev'

        return 'stable'

    def parse_name_version_pairs(self, pairs):
        result = []

        for pair in pairs:
            pair = re.sub('^([^=: ]+)[=: ](.*)$', '\\1 \\2', pair.strip())

            if ' ' in pair:
                name, version = pair.split(' ', 2)

                result.append({
                    'name': name,
                    'version': version
                })
            else:
                result.append({
                    'name': pair,
                    'version': '*'
                })

        return result
