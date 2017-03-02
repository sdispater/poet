# -*- coding: utf-8 -*-

import re
import os
import toml
import subprocess

from .exceptions.sonnet import MissingElement, InvalidElement
from .version_parser import VersionParser
from .build import Builder
from .package import Dependency


class Sonnet(object):

    EXCLUDES = ()

    def __init__(self, path, builder=Builder()):
        self._path = path
        self._dir = os.path.dirname(path)
        self._builder = builder
        self._git_config = None
        self._dependencies = None
        self._dev_dependencies = None

        with open(self._path) as f:
            self._config = toml.loads(f.read())

        self._readme = None

    @property
    def base_dir(self):
        return self._dir

    @property
    def git_config(self):
        if self._git_config is not None:
            return self._git_config

        config_list = subprocess.check_output(
            ['git', 'config', '-l']
        )

        self._git_config = {}

        m = re.findall('(?ms)^([^=]+)=(.*?)$', config_list)
        if m:
            for group in m:
                self._git_config[group[0]] = group[1]

        return self._git_config

    @property
    def ignore(self):
        ignore_files = [
            '.gitignore'
        ]

        ignore = []

        for filename in ignore_files:
            with open(os.path.join(self._dir, filename)) as fd:
                for line in fd.readlines():
                    if re.match('^\s*#.*$', line):
                        continue

                    ignore.append(line.strip())

        return ignore

    @property
    def name(self):
        return self._config['package']['name']

    @property
    def version(self):
        return self._config['package']['version']

    @property
    def description(self):
        return self._config['package']['description']

    @property
    def authors(self):
        return self._config['package']['authors']

    @property
    def homepage(self):
        return self._config['package'].get('homepage')

    @property
    def repository(self):
        return self._config['package'].get('repository')

    @property
    def keywords(self):
        return self._config['package'].get('keywords', [])

    @property
    def python_versions(self):
        return self._config['package']['python']

    @property
    def dependencies(self):
        if self._dependencies is None:
            self._dependencies = self._get_dependencies(self._config.get('dependencies', {}))

        return self._dependencies

    @property
    def dev_dependencies(self):
        if self._dev_dependencies is None:
            self._dev_dependencies = self._get_dependencies(self._config.get('dev-dependencies', {}))

        return self._dev_dependencies

    @property
    def scripts(self):
        return self._config.get('scripts', {})

    @property
    def license(self):
        return self._config['package'].get('license')

    @property
    def readme(self):
        if self._readme is None:
            with open(os.path.join(self._dir, self._config['package']['readme'])) as f:
                self._readme = f.read()

        return self._readme

    @property
    def include(self):
        return self._config['package'].get('include', [self.name])

    @property
    def exclude(self):
        return self._config['package'].get('exclude', []) + list(self.EXCLUDES)

    def build(self, **options):
        self.check()

        self._builder.build(self, **options)

    def check(self):
        package = self._config.get('package')
        if not package:
            raise MissingElement('package')

        self._check_package(package)

        dependencies = self._config.get('dependencies')
        if dependencies:
            self._check_dependencies(dependencies)

        dev_dependencies = self._config.get('dev-dependencies')
        if dev_dependencies:
            self._check_dependencies(dev_dependencies)

    def _check_package(self, package):
        name = package.get('name')
        if not name:
            raise MissingElement('package.name')

        version = package.get('version')
        if not version:
            raise MissingElement('package.version')

        authors = package.get('authors')
        if not authors:
            raise MissingElement('package.authors')

        if not isinstance(authors, list):
            raise InvalidElement('package.authors', 'it must be a list')

        license = package.get('license')
        if license:
            self._check_license(license)

        readme = package.get('readme')
        if not readme:
            raise MissingElement('package.readme')

        self._check_readme(readme)

    def _check_license(self, license):
        pass

    def _check_readme(self, readme):
        readme_path = os.path.join(self._dir, readme)

        if not os.path.exists(readme_path):
            raise InvalidElement('package.readme', 'invalid path provided')

        _, ext = os.path.splitext(readme)

        if ext not in ['.md', '.rst', '.txt']:
            raise InvalidElement('package.readme', 'extension [{}] is not supported'.format(ext))

    def _check_dependencies(self, dependencies):
        for name, constraint in dependencies.items():
            self._check_package_constraint(name, constraint)

    def _check_package_constraint(self, name, constraint):
        message = 'Invalid constraint [{}]'.format(constraint)

        if isinstance(constraint, dict):
            return self._check_vcs_constraint(name, constraint)
        else:
            try:
                return VersionParser().parse_constraints(constraint)
            except ValueError:
                pass

        raise InvalidElement('dependencies.{}'.format(name), message)

    def _check_vcs_constraint(self, name, constraint):
        if 'git' in constraint:
            self._check_git_constraint(name, constraint)

    def _check_git_constraint(self, name, constraint):
        if all(['branch' not in constraint, 'rev' not in constraint, 'tag' not in constraint]):
            raise InvalidElement(
                'dependencies.{}'.format(name),
                'Git constraint should have one of [branch, rev, tag]'
            )

    def _get_dependencies(self, dependencies):
        keys = sorted(list(dependencies.keys()))

        return [Dependency(k, dependencies[k]) for k in keys]
