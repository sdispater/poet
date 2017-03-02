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
    Tool to transform a sonnet file to a setup() instruction.
    """

    AUTHOR_REGEX = re.compile('(?u)^(?P<name>[- .,\w\d\'’"()]+) <(?P<email>.+?)>$')

    PYTHON_VERSIONS = {
        2: ['2.6', '2.7'],
        3: ['3.0', '3.1', '3.2', '3.3', '3.4', '3.5', '3.6']
    }

    def build(self, sonnet, **options):
        """
        Builds a sonnet.

        :param sonnet: The sonnet to build.
        :type sonnet: sonnet.sonnet.Sonnet
        """
        setup_kwargs = self._setup(sonnet, **options)

        setup = os.path.join(sonnet.base_dir, 'setup.py')
        self._write_setup(setup_kwargs, setup)

        setup_kwargs['script_name'] = 'setup.py'

        try:
            dist = Distribution(setup_kwargs)
            dist.run_command('sdist')
        except Exception:
            raise
        finally:
            os.unlink(setup)

    def _setup(self, sonnet, **options):
        setup_kwargs = {
            'name': sonnet.name,
            'version': sonnet.version,
            'description': sonnet.description,
            'long_description': sonnet.readme
        }

        setup_kwargs.update(self._author(sonnet))

        setup_kwargs['url'] = self._url(sonnet)

        setup_kwargs['license'] = sonnet.license

        setup_kwargs['keywords'] = self._keywords(sonnet)

        setup_kwargs['classifiers'] = self._classifiers(sonnet)

        setup_kwargs['entry_points'] = self._entry_points(sonnet)

        setup_kwargs['install_requires'] = self._install_requires(sonnet)

        setup_kwargs.update(self._packages(sonnet))

        return setup_kwargs

    def _author(self, sonnet):
        m = self.AUTHOR_REGEX.match(sonnet.authors[0])

        return {
            'author': m.group('name'),
            'author_email': m.group('email')
        }

    def _url(self, sonnet):
        return sonnet.homepage or sonnet.repository

    def _keywords(self, sonnet):
        return ' '.join(sonnet.keywords or [])

    def _classifiers(self, sonnet):
        classifiers = []

        classifiers += self._classifiers_versions(sonnet)

        return classifiers

    def _classifiers_versions(self, sonnet):
        classifers = ['Programming Language :: Python']
        compatible_versions = {}

        for python in sonnet.python_versions:
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

    def _entry_points(self, sonnet):
        entry_points = {
            'console_scripts': []
        }

        for name, script in sonnet.scripts.items():
            entry_points['console_scripts'].append('{}={}:{}'.format(name, sonnet.name, script))

        return entry_points

    def _install_requires(self, sonnet):
        requires = []
        dependencies = sonnet.dependencies

        for dependency in dependencies:
            requires.append(dependency.normalized_name)

        return requires

    def _packages(self, sonnet):
        includes = sonnet.include
        packages = []
        modules = []
        crawled = []
        excluded = []

        for exclude in sonnet.exclude + sonnet.ignore:
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
                    #packages.append(dir.rstrip('/').replace('/', '.'))

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
