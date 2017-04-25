# -*- coding: utf-8 -*-

from semantic_version import Spec, SpecItem, Version

from ..version_parser import VersionParser


class Dependency(object):

    def __init__(self, name, constraint, category='main'):
        self._name = name
        self._constraint = constraint
        self._optional = False
        self._accepts_prereleases = False
        self._category = category
        self._python = [Spec('*')]

        if isinstance(constraint, dict):
            if 'python' in constraint:
                python = constraint['python']

                if not isinstance(python, list):
                    python = [python]

                self._python = [Spec(p) for p in python]

            if 'optional' in constraint:
                self._optional = constraint['optional']

            if 'version' in constraint:
                self._constraint = constraint['version']

        self._normalized_constraint = self._normalize(constraint)

    @property
    def name(self):
        return self._name
    
    @property
    def optional(self):
        return self._optional

    @property
    def constraint(self):
        return self._constraint

    @property
    def category(self):
        return self._category

    @property
    def python(self):
        return self._python

    @property
    def pretty_constraint(self):
        constraint = self._constraint

        if self.is_vcs_dependency():
            if 'git' in self._constraint:
                vcs_kind = 'branch'
                if 'rev' in self._constraint:
                    vcs_kind = 'rev'
                    version = self._constraint['rev']
                elif 'tag' in constraint:
                    vcs_kind = 'tag'
                    version = self._constraint['tag']
                else:
                    version = self._constraint.get('branch', 'master')

                constraint = '{} {}'.format(vcs_kind, version)
            else:
                raise ValueError('Unsupport VCS.')

        return constraint

    @property
    def normalized_constraint(self):
        return self._normalized_constraint
    
    @property
    def normalized_name(self):
        normalized_name = self._name
        normalized_constraint = self.normalized_constraint

        if normalized_constraint:
            normalized_name += normalized_constraint

        return normalized_name

    def is_vcs_dependency(self):
        return isinstance(self._constraint, dict) and 'git' in self._constraint

    def accepts_prereleases(self):
        return self._accepts_prereleases

    def is_python_restricted(self):
        return self._python != [Spec('*')]

    def _normalize(self, constraint):
        """
        Normalizes the constraint so that it can be understood
        by the underlying system.
        
        :param constraint: The dependency constraint.
        :type constraint: str or dict
        
        :rtype: str
        """
        if self.is_vcs_dependency():
            # Any VCS dependency is considered prerelease
            self._is_prerelease = True

            return self._normalize_vcs_constraint(constraint)

        version = constraint
        if isinstance(version, dict):
            version = version['version']

        constraint = self._spec(version)
        normalized = []

        for spec in constraint.specs:
            version = spec.spec

            if VersionParser.parse_stability(version) == 'dev':
                self._accepts_prereleases = True

            major, minor, patch, prerelease = (
                version.major, version.minor, version.patch, version.prerelease
            )
            current = '{}.{}.{}'.format(major, minor or 0, patch or 0)
            current = Version(current)

            if spec.kind == SpecItem.KIND_CARET:
                if current.major != 0 or minor is None:
                    upper = current.next_major()
                elif current.minor != 0 or patch is None:
                    upper = current.next_minor()
                else:
                    upper = current.next_patch()

                if prerelease:
                    current = str(current) + '{}'.format(''.join(prerelease))

                normalized.append('>={},<{}'.format(current, upper))
            elif spec.kind == SpecItem.KIND_TILDE:
                if minor is None and patch is None:
                    upper = current.next_major()
                else:
                    upper = current.next_minor()

                upper = '{}.{}.{}'.format(*upper)

                normalized.append('>={},<{}'.format(current, upper))

                if prerelease:
                    current = str(current) + '{}'.format(''.join(prerelease))
            else:
                current = spec.kind + str(current)
                if prerelease:
                    current += '{}'.format(''.join(prerelease))

                normalized.append(current)

        return ','.join(normalized)

    def _normalize_vcs_constraint(self, constraint):
        # Neither setuptools nor distutils support VCS constraint
        # So by default we return nothing
        return ''

    def _spec(self, version):
        try:
            return Spec(version)
        except ValueError:
            return Spec(str(Version.coerce(version)))

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.normalized_name)
