# -*- coding: utf-8 -*-

from .version_parser import VersionParser


class VersionSelector(object):

    def __init__(self, repository, parser=VersionParser()):
        self._repository = repository
        self._parser = parser

    def find_best_candidate(self, package_name, target_package_version=None,
                            preferred_stability='stable'):
        if target_package_version:
            constraint = self._parser.parse_constraints(target_package_version)
        else:
            constraint = None

        candidates = self._repository.find_packages(package_name, constraint)

        if not candidates:
            return False

        # Select highest version if we have many
        package = candidates[0]
        for candidate in candidates:
            # Select highest version of the two
            if package.version < candidate.version:
                package = candidate

        return package

    def find_recommended_require_version(self, package):
        version = package.version

        if not package.is_dev():
            return self._transform_version(version, package.pretty_version, package.stability)

    def _transform_version(self, version, pretty_version, stability):
        # attempt to transform 2.1.1 to 2.1
        # this allows you to upgrade through minor versions
        if str(version) != pretty_version:
            # Not semver
            return pretty_version

        # append stability flag if not stable
        if stability != 'stable':
            version += '@{}'.format(stability)

        return '^{}.{}'.format(version.major, version.minor)

