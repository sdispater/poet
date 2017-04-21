# -*- coding: utf-8 -*-

import re
import os
import toml
import warnings

try:
    import pypandoc
except ImportError:
    pypandoc = None

from packaging.version import Version as PackageVersion

from .exceptions.poet import MissingElement, InvalidElement
from .version_parser import VersionParser
from .build import Builder
from .package import Dependency, PipDependency
from .utils.helpers import call


class Poet(object):

    EXCLUDES = ()
    INCLUDES = ()

    def __init__(self, path, builder=Builder()):
        self._path = path
        self._dir = os.path.realpath(os.path.dirname(path))
        self._builder = builder
        self._git_config = None

        self._name = None
        self._version = None
        self._description = None
        self._authors = []
        self._homepage = None
        self._repository = None
        self._keywords = []
        self._python_versions = []
        self._dependencies = []
        self._dev_dependencies = []
        self._pip_dependencies = []
        self._pip_dev_dependencies = []
        self._features = {}
        self._scripts = {}
        self._entry_points = {}
        self._license = None
        self._readme = None
        self._include = []
        self._exclude = []
        self._extensions = {}

        with open(self._path) as f:
            self._config = toml.loads(f.read())

        self.load()

    @property
    def base_dir(self):
        return self._dir

    @property
    def git_config(self):
        if self._git_config is not None:
            return self._git_config

        config_list = call(['git', 'config', '-l'])

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
            filepath = os.path.join(self._dir, filename)
            if not os.path.exists(filepath):
                continue

            with open(filepath) as fd:
                for line in fd.readlines():
                    if re.match('^\s*#.*$', line):
                        continue

                    ignore.append(line.strip())

        return ignore

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def normalized_version(self):
        """
        Return a PEP 440 compatible version.
        
        :rtype: str
        """
        return str(PackageVersion(self._version))

    @property
    def description(self):
        return self._description

    @property
    def authors(self):
        return self._authors

    @property
    def homepage(self):
        return self._homepage

    @property
    def repository(self):
        return self._repository

    @property
    def keywords(self):
        return self._keywords

    @property
    def python_versions(self):
        return self._python_versions

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def dev_dependencies(self):
        return self._dev_dependencies

    @property
    def pip_dependencies(self):
        return self._pip_dependencies

    @property
    def pip_dev_dependencies(self):
        return self._pip_dev_dependencies

    @property
    def features(self):
        return self._features

    @property
    def scripts(self):
        return self._scripts

    @property
    def entry_points(self):
        return self._entry_points

    @property
    def license(self):
        return self._license

    @property
    def readme(self):
        return self._readme

    @property
    def include(self):
        return self._include

    @property
    def exclude(self):
        return self._exclude

    @property
    def extensions(self):
        return self._extensions

    @property
    def lock_file(self):
        return os.path.join(self._dir, 'poetry.lock')

    @property
    def lock(self):
        from .lock import Lock

        return Lock(self.lock_file)

    @property
    def path(self):
        return self._path

    @property
    def archive(self):
        return '{}-{}.tar.gz'.format(self.name, self.normalized_version)

    def is_prerelease(self):
        return Ver

    def load(self):
        """
        Load data from the config.
        """
        self._name = self._config['package']['name']
        self._version = self._config['package']['version']
        self._description = self._config['package']['description']
        self._authors = self._config['package']['authors']
        self._license = self._config['package'].get('license')
        self._homepage = self._config['package'].get('homepage')
        self._repository = self._config['package'].get('repository')
        self._keywords = self._config['package'].get('keywords', [])
        self._python_versions = self._config['package']['python']
        self._dependencies = self._get_dependencies(self._config.get('dependencies', {}))
        self._dev_dependencies = self._get_dependencies(self._config.get('dev-dependencies', {}), category='dev')
        self._pip_dependencies = self._get_dependencies(self._config.get('dependencies', {}), 'pip')
        self._pip_dev_dependencies = self._get_dependencies(self._config.get('dev-dependencies', {}), 'pip', category='dev')
        self._features = self._config.get('features', {})
        self._scripts = self._config.get('scripts', {})
        self._entry_points = self._config.get('entry-points', {})

        self._load_readme()

        self._include = self._config['package'].get('include', []) + list(self.INCLUDES)
        self._exclude = self._config['package'].get('exclude', []) + list(self.EXCLUDES)

        self._extensions = self._config.get('extensions', {})

    def _load_readme(self):
        readme = self._config['package']['readme']
        readme_path = os.path.join(self._dir, readme)

        if self.has_markdown_readme():
            if not pypandoc:
                warnings.warn(
                    'Markdown README files require the pandoc utility '
                    'and the pypandoc package.'
                )
            else:
                self._readme = pypandoc.convert_file(readme_path, 'rst')
        else:
            with open(readme_path) as f:
                self._readme = f.read()

    def has_markdown_readme(self):
        """
        Return whether the README is a markdown one.

        :rtype: boolean
        """
        readme = self._config['package']['readme']
        _, ext = os.path.splitext(readme)

        return ext == '.md'

    def is_lock(self):
        return False

    def build(self, **options):
        self.check()

        self._builder.build(self, **options)

    def check(self):
        """
        Checks if the poetry.toml file is valid.
        """
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
        if 'name' not in package:
            raise MissingElement('package.name')

        if 'version' not in package:
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

    def _get_dependencies(self, dependencies, kind='default', category='main'):
        keys = sorted(list(dependencies.keys()))

        klass = Dependency
        if kind == 'pip':
            klass = PipDependency

        return [klass(k, dependencies[k], category=category) for k in keys]
