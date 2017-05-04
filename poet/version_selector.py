# -*- coding: utf-8 -*-

from .package import Package
from .version_parser import VersionParser


class VersionSelector(object):

    def __init__(self, repository, parser=VersionParser()):
        self._repository = repository
        self._parser = parser

    def find_best_candidate(self, package_name, target_package_version=None,
                            preferred_stability='stable'):
        """
        Given a package name and optional version,
        returns the latest Package that matches
        
        :param package_name: The name of the package
        :type package_name: str
        
        :param target_package_version: Optional target version/constraint
        :type target_package_version: str
        
        :param preferred_stability: The preferred stability of the package
        :type preferred_stability: str
        
        :rtype: poet.package.Package 
        """
        if target_package_version:
            constraint = self._parser.parse_constraints(target_package_version)
        else:
            constraint = None

        candidates = self._repository.find_packages(package_name, constraint)

        if not candidates:
            return False

        # Select highest version if we have many
        package = candidates[0]
        min_stability = Package.STABILITIES[preferred_stability]
        for candidate in candidates:
            candidate_priority = candidate.stability_priority
            current_priority = package.stability_priority

            # candidate is less stable than our preferred stability,
            # and we have a package that is more stable than it, so we skip it
            if min_stability < candidate_priority and current_priority < candidate_priority:
                continue

            # candidate is more stable than our preferred stability,
            # and current package is less stable than preferred stability,
            # then we select the candidate always
            if min_stability >= candidate_priority and min_stability < current_priority:
                package = candidate
                continue

            # Select highest version of the two
            if package.version < candidate.version:
                package = candidate

        return package

    def find_recommended_require_version(self, package):
        version = package.version

        return self._transform_version(version, package.pretty_version, package.stability)

    def _transform_version(self, version, pretty_version, stability):
        # attempt to transform 2.1.1 to 2.1
        # this allows you to upgrade through minor versions
        if str(version) != pretty_version:
            # Not semver
            return pretty_version

        return '^{}.{}'.format(version.major, version.minor)
