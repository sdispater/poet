# -*- coding: utf-8 -*-

from pip.req import InstallRequirement
from .dependency import Dependency


class PipDependency(Dependency):

    def __init__(self, name, constraint, checksum=None):
        super(PipDependency, self).__init__(name, constraint)

        self._checksum = checksum

    @property
    def checksum(self):
        return self._checksum

    @property
    def normalized_name(self):
        normalized_name = self._name
        normalized_constraint = self.normalized_constraint

        if normalized_constraint:
            if self.is_vcs_dependency():
                normalized_name = normalized_constraint
            else:
                normalized_name += normalized_constraint

        return normalized_name

    def as_requirement(self):
        if self.is_vcs_dependency():
            return InstallRequirement.from_editable(self.normalized_name)

        return InstallRequirement.from_line(self.normalized_name)

    def _normalize_vcs_constraint(self, constraint):
        if 'git' in constraint:
            repo = constraint['git']
            if 'branch' in constraint:
                revision = constraint['branch']
            elif 'tag' in constraint:
                revision = constraint['tag']
            else:
                revision = constraint['rev']

            if not repo.startswith('git+'):
                repo = 'git+' + repo

            return '{}@{}#egg={}'.format(repo, revision, self._name)

        raise ValueError('Unsupport VCS.')
