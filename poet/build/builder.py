# -*- coding: utf-8 -*-

import os
import re
import glob
import tempfile

from setuptools.dist import Distribution
from semantic_version import Spec, Version


SETUP_TEMPLATE = """from setuptools import setup

kwargs = {}

setup(**kwargs)
"""


class Builder(object):
    """
    Tool to transform a poet file to a setup() instruction.
    """

    AUTHOR_REGEX = re.compile('(?u)^(?P<name>[- .,\w\d\'’"()]+) <(?P<email>.+?)>$')

    PYTHON_VERSIONS = {
        2: ['2.6', '2.7'],
        3: ['3.0', '3.1', '3.2', '3.3', '3.4', '3.5', '3.6']
    }

    def __init__(self):
        self._manifest = []

    def build(self, poet, **options):
        """
        Builds a poet.

        :param poet: The poet to build.
        :type poet: poet.poet.Poet
        """
        setup_kwargs = self._setup(poet, **options)

        setup = os.path.join(poet.base_dir, 'setup.py')
        manifest = os.path.join(poet.base_dir, 'MANIFEST.in')
        self._write_setup(setup_kwargs, setup)
        self._write_manifest(manifest)

        try:
            dist = Distribution(setup_kwargs)
            dist.run_command('sdist')
        except Exception:
            raise
        finally:
            os.unlink(setup)
            os.unlink(manifest)

    def _setup(self, poet, **options):
        setup_kwargs = {
            'name': poet.name,
            'version': poet.version,
            'description': poet.description,
            'long_description': poet.readme,
            'include_package_data': True,
            'script_name': 'setup.py'
        }

        setup_kwargs.update(self._author(poet))

        setup_kwargs['url'] = self._url(poet)

        setup_kwargs['license'] = poet.license

        setup_kwargs['keywords'] = self._keywords(poet)

        setup_kwargs['classifiers'] = self._classifiers(poet)

        setup_kwargs['entry_points'] = self._entry_points(poet)

        setup_kwargs['install_requires'] = self._install_requires(poet)

        setup_kwargs.update(self._packages(poet))

        return setup_kwargs

    def _author(self, poet):
        m = self.AUTHOR_REGEX.match(poet.authors[0])

        return {
            'author': m.group('name'),
            'author_email': m.group('email')
        }

    def _url(self, poet):
        return poet.homepage or poet.repository

    def _keywords(self, poet):
        return ' '.join(poet.keywords or [])

    def _classifiers(self, poet):
        classifiers = []

        classifiers += self._classifiers_versions(poet)

        return classifiers

    def _classifiers_versions(self, poet):
        classifers = ['Programming Language :: Python']
        compatible_versions = {}

        for python in poet.python_versions:
            constraint = Spec(python)

            for major in [2, 3]:
                available_versions = self.PYTHON_VERSIONS[major]

                for version in available_versions:
                    if Version.coerce(version) in constraint:
                        if major not in compatible_versions:
                            compatible_versions[major] = []

                        compatible_versions[major].append(version)

        for major in sorted(list(compatible_versions.keys())):
            versions = compatible_versions[major]
            classifer_template = 'Programming Language :: Python :: {}'

            classifers.append(classifer_template.format(major))

            for version in versions:
                classifers.append(classifer_template.format(version))

        return classifers

    def _entry_points(self, poet):
        entry_points = {
            'console_scripts': []
        }

        for name, script in poet.scripts.items():
            entry_points['console_scripts'].append('{}={}:{}'.format(name, poet.name, script))

        return entry_points

    def _install_requires(self, poet):
        requires = []
        dependencies = poet.dependencies

        for dependency in dependencies:
            requires.append(dependency.normalized_name)

        return requires

    def _packages(self, poet):
        includes = poet.include
        packages = []
        modules = []
        crawled = []
        excluded = []

        for exclude in poet.exclude + poet.ignore:
            for exc in glob.glob(exclude, recursive=True):
                if exc.startswith('/'):
                    exc = exc[1:]

                if exc.endswith('.py'):
                    excluded.append(exc.replace('.py', '').replace('/', '.'))

        for include in includes:
            elements = glob.glob(include, recursive=True)
            dirs = [d for d in elements if os.path.isdir(d)]
            others = [d for d in elements if not os.path.isdir(d)]

            for dir in dirs:
                if dir in crawled:
                    continue

                # We have a package
                if os.path.exists(os.path.join(dir, '__init__.py')):
                    children = [
                        c.replace('.py', '').replace('/', '.')
                        for c in glob.glob(os.path.join(dir, '*.py'))
                        if os.path.basename(c) != '__init__.py'
                    ]

                    modules += children
                    crawled += children

                crawled.append(dir)

            for element in others:
                if element in crawled:
                    continue

                if element.endswith('.py') and os.path.basename(element) != '__init__.py':
                    modules.append(element.replace('.py', '').replace('/', '.'))
                elif os.path.basename(element) != '__init__.py' and '__pycache__' not in element:
                    # Non Python file, add them to data
                    self._manifest.append('include {}'.format(element))

                crawled.append(element)

        packages = [p for p in packages if p not in excluded]
        modules = [m for m in modules if m not in excluded]

        return {
            'packages': packages,
            'py_modules': modules
        }

    def _write_setup(self, setup, dest):
        with open(dest, 'w') as f:
            f.write(SETUP_TEMPLATE.format(repr(setup)))

    def _write_manifest(self, manifest):
        with open(manifest, 'w') as f:
            f.writelines(self._manifest)
