# -*- coding: utf-8 -*-

import os
import re

from setuptools import Extension
from setuptools.dist import Distribution
from pip.commands.wheel import WheelCommand
from semantic_version import Spec, Version

from .._compat import Path, PY2, encode, decode


SETUP_TEMPLATE = """# -*- coding: utf-8 -*-

from setuptools import setup

kwargs = dict(
    name={name},
    version={version},
    description={description},
    long_description={long_description},
    author={author},
    author_email={author_email},
    url={url},
    license={license},
    keywords={keywords},
    classifiers={classifiers},
    entry_points={entry_points},
    install_requires={install_requires},
    tests_require={tests_require},
    extras_require={extras_require},
    packages={packages},
    py_modules={py_modules},
    script_name='setup.py',
    include_package_data=True
)
"""

EXTENSIONS_TEMPLATE = """
from setuptools import Extension

kwargs['ext_modules'] = [
    {extensions}
]
"""

EXTENSION_TEMPLATE = """Extension(
        '{module}',
        {source}
    )"""


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

        readme = None
        if poet.has_markdown_readme():
            readme = os.path.join(poet.base_dir, 'README.rst')
            if os.path.exists(readme):
                readme = None
            else:
                self._write_readme(readme, setup_kwargs['long_description'])

        self._manifest.append('include README.rst')

        self._write_manifest(manifest)

        try:
            dist = Distribution(setup_kwargs)
            dist.run_command('sdist')
        except Exception:
            raise
        finally:
            os.unlink(setup)
            os.unlink(manifest)

            if readme:
                os.unlink(readme)

        # Building wheel if necessary
        if not options.get('no_wheels'):
            command = WheelCommand()
            command_args = ['--no-index', '--no-deps', '--wheel-dir', 'dist', 'dist/{}'.format(poet.archive)]

            if options.get('universal', True):
                command_args.append('--build-option=--universal')

            command.main(command_args)

    def _setup(self, poet, **options):
        """
        Builds the setup kwargs base on the Poet instance
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: dict
        """
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
        setup_kwargs['tests_require'] = self._tests_require(poet)
        setup_kwargs['extras_require'] = self._extras_require(poet)

        setup_kwargs.update(self._packages(poet))

        # Extensions
        setup_kwargs.update(self._ext_modules(poet))

        return setup_kwargs

    def _author(self, poet):
        m = self.AUTHOR_REGEX.match(poet.authors[0])

        name = m.group('name')
        email = m.group('email')

        if PY2:
            name = encode(name)
            email = encode(email)

        return {
            'author': name,
            'author_email': email
        }

    def _url(self, poet):
        return poet.homepage or poet.repository

    def _keywords(self, poet):
        return ' '.join(poet.keywords or [])

    def _classifiers(self, poet):
        """
        Builds the classifiers list from the
        specified Python versions.
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: list
        """
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
        """
        Builds the entry points
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: list
        """
        entry_points = {
            'console_scripts': []
        }

        for name, script in poet.scripts.items():
            entry_points['console_scripts'].append('{}={}'.format(name, script))

        return entry_points

    def _install_requires(self, poet):
        """
        Builds the dependencies list.
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: dict
        """
        requires = []
        dependencies = poet.dependencies

        for dependency in dependencies:
            if dependency.optional:
                continue

            requires.append(dependency.normalized_name)

        return requires

    def _tests_require(self, poet):
        """
        Builds the dev dependencies list.
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: dict
        """
        requires = []
        dependencies = poet.dev_dependencies

        for dependency in dependencies:
            if dependency.optional:
                continue

            requires.append(dependency.normalized_name)

        return requires

    def _extras_require(self, poet):
        """
        Builds the extras dictionary from
        the configured features.
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: dict
        """
        if not poet.features:
            return {}

        extras = {}
        for feature_name, featured_packages in poet.features.items():
            extras[feature_name] = []

            for package in featured_packages:
                for dep in poet.dependencies:
                    if dep.name == package:
                        extras[feature_name].append(dep.normalized_name)

        return extras

    def _packages(self, poet):
        """
        Builds the packages and modules list
        based on the include and exclude sections.
        
        It will also register files that need to be put
        in the MANIFEST.in file.
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: dict 
        """
        includes = poet.include
        packages = []
        modules = []
        crawled = []
        excluded = []
        base_path = Path(poet.base_dir)

        for exclude in poet.exclude + poet.ignore:
            if not exclude:
                continue

            if exclude.startswith('/'):
                exclude = exclude[1:]

            for exc in base_path.glob(exclude):
                if exc.suffix == '.py':
                    exc = exc.relative_to(base_path)
                    excluded.append('.'.join(exc.with_suffix('').parts))

        for include in includes:
            dirs = []
            others = []
            for element in base_path.glob(include):
                if element.is_dir():
                    dirs.append(element.relative_to(base_path))
                else:
                    others.append(element.relative_to(base_path))

            m = re.match('^(.+)/\*\*/\*(\..+)?$', include)
            if m:
                # {dir}/**/* will not take the root directory
                # So we add it
                dirs.insert(0, Path(m.group(1)))

            for dir in dirs:
                package = '.'.join(dir.parts)

                if dir in crawled:
                    continue

                # We have a package
                real_dir = base_path / dir
                if (real_dir / '__init__.py').exists():
                    children = [
                        c.relative_to(base_path) for c in real_dir.glob('*.py')
                    ]

                    filtered_children = [c for c in children if '.'.join(c.parts) not in excluded]
                    if children == filtered_children:
                        # If none of the children are excluded
                        # We have a full package
                        packages.append(package)
                    else:
                        modules += ['.'.join(c.parts) for c in filtered_children]

                    crawled += children

                crawled.append(dir)

            for element in others:
                if element in crawled or element.suffix == '.pyc':
                    continue

                if element.suffix == '.py' and element.name != '__init__.py':
                    modules.append('.'.join(element.with_suffix('').parts))
                elif element.suffix not in ['.py', '.pyc'] and '__pycache__' not in element.parts:
                    # Non Python file, add them to data
                    self._manifest.append('include {}\n'.format(element.as_posix()))
                elif element.name == '__init__.py':
                    dir = element.parent
                    real_dir = base_path / dir
                    children = [
                        c.relative_to(base_path)
                        for c in real_dir.glob('*.py')
                        if c.name != '__init__.py'
                    ]

                    if not children and dir not in crawled:
                        # We actually have a package
                        packages.append('.'.join(dir.parts))

                        crawled.append(dir)

                crawled.append(element)

        packages = [p for p in packages if p not in excluded]
        modules = [m for m in modules if m not in excluded]

        return {
            'packages': packages,
            'py_modules': modules
        }

    def _ext_modules(self, poet):
        extensions = []
        for module, source in poet.extensions.items():
            if not isinstance(source, list):
                source = [source]

            ext = Extension(module, source)
            extensions.append(ext)

        return {
            'ext_modules': extensions
        }

    def _write_setup(self, setup, dest):
        parameters = setup.copy()

        extensions = []
        if parameters['ext_modules']:
            for extension in parameters['ext_modules']:
                module = extension.name
                source = extension.sources

                extensions.append(
                    EXTENSION_TEMPLATE.format(
                        module=module,
                        source=repr(source)
                    )
                )

            del parameters['ext_modules']

        for key in parameters.keys():
            value = parameters[key]

            if value is not None:
                parameters[key] = repr(value)

        with open(dest, 'w') as f:
            f.write(SETUP_TEMPLATE.format(**parameters))

            if extensions:
                f.write(EXTENSIONS_TEMPLATE.format(extensions='\n    '.join(extensions)))

            f.write('\nsetup(**kwargs)')

    def _write_manifest(self, manifest):
        with open(manifest, 'w') as f:
            f.writelines(self._manifest)

    def _write_readme(self, readme, content):
        with open(readme, 'w') as f:
            f.write(content)

