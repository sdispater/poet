# -*- coding: utf-8 -*-

from semantic_version import Spec, SpecItem, Version


class Dependency(object):

    def __init__(self, name, constraint):
        self._name = name
        self._constraint = constraint
        self._normalized_constraint = self._normalize(constraint)

    @property
    def name(self):
        return self._name

    @property
    def constraint(self):
        return self._constraint

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
        return isinstance(self._constraint, dict)

    def _normalize(self, constraint):
        if self.is_vcs_dependency():
            return self._normalize_vcs_constraint(constraint)

        constraint = Spec(constraint)
        normalized = []

        for spec in constraint.specs:
            major, minor, patch = spec.spec.major, spec.spec.minor, spec.spec.patch
            current = '{}.{}.{}'.format(major, minor or 0, patch or 0)
            current = Version(current)

            if spec.kind == SpecItem.KIND_CARET:
                if current.major != 0 or minor is None:
                    upper = current.next_major()
                elif current.minor != 0 or patch is None:
                    upper = current.next_minor()
                else:
                    upper = current.next_patch()

                normalized.append('>={},<{}'.format(current, upper))
            elif spec.kind == SpecItem.KIND_TILDE:
                if minor is None and patch is None:
                    upper = current.next_major()
                else:
                    upper = current.next_minor()

                upper = '{}.{}.{}'.format(*upper)

                normalized.append('>={},<{}'.format(current, upper))
            else:
                normalized.append(str(spec))

        return ','.join(normalized)

    def _normalize_vcs_constraint(self, constraint):
        # Neither setuptools nor distutils support VCS constraint
        # So by default we return nothing
        return

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.normalized_name)
