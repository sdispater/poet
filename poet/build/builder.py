# -*- coding: utf-8 -*-

import os
import re
import warnings

from setuptools.dist import Distribution
from setuptools.extension import Extension
from pip.commands.wheel import WheelCommand
from pip.status_codes import SUCCESS
from semantic_version import Spec, Version

from .._compat import Path, PY2, encode
from ..utils.helpers import template


class Builder(object):
    """
    Tool to transform a poet file to a setup() instruction.
    
    It also creates the MANIFEST.in file if necessary.
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
        Builds a package from a Poet instance

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
            command_args = [
                '--no-index',
                '--no-deps',
                '-q',
                '--wheel-dir', 'dist',
                'dist/{}'.format(poet.archive)
            ]

            if options.get('universal', True):
                command_args.append('--build-option=--universal')

            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                status = command.main(command_args)

            if status != SUCCESS:
                raise Exception('An error occurred while executing command.')

    def _setup(self, poet, **options):
        """
        Builds the setup kwargs base on the Poet instance
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: dict
        """
        setup_kwargs = {
            'name': poet.name,
            'version': poet.normalized_version,
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
        """
        Build the author information from a Poet instance.
        
        Transforms a author in the form "name <email>" into
        a proper dictionary.
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: dict
        """
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

        # Generic entry points
        for category, entry_points in poet.entry_points.items():
            entry_points[category] = []

            for name, script in entry_points.items():
                entry_points[category].append('{} = {}'.format(name, script))

        # Console scripts entry points
        for name, script in poet.scripts.items():
            entry_points['console_scripts'].append('{} = {}'.format(name, script))

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
        package_dirs = {}
        crawled = []
        excluded = []
        root = Path(poet.base_dir)

        for exclude in poet.exclude + poet.ignore:
            if not exclude:
                continue

            if exclude.startswith('/'):
                exclude = exclude[1:]

            for exc in root.glob(exclude):
                if exc.suffix == '.py':
                    exc = exc.relative_to(root)
                    excluded.append('.'.join(exc.with_suffix('').parts))

        if not isinstance(includes, list):
            includes = [includes]

        for include in includes:
            if isinstance(include, dict):
                settings = self._find_packages_from(
                    root,
                    include['from'],
                    include['include'],
                    include.get('as', ''),
                    excluded=excluded,
                    crawled=crawled
                )
            else:
                settings = self._find_packages_from(
                    root,
                    '',
                    include,
                    excluded=excluded,
                    crawled=crawled
                )

            packages += settings['packages']
            modules += settings['modules']
            package_dirs.update(settings.get('package_dirs', {}))

        packages = [p for p in packages if p not in excluded]
        modules = [m for m in modules if m not in excluded]

        settings = {
            'packages': packages,
            'py_modules': modules
        }

        package_dir = {}
        for package_name, directory in package_dirs.items():
            package_dir[package_name] = directory.as_posix()

        if package_dir:
            settings['package_dir'] = package_dir

        return settings

    def _find_packages_from(self, root, base_dir, includes,
                            package_name=None, excluded=None, crawled=None):
        package_dirs = {}
        packages = []
        modules = []

        if package_name is not None:
            package_dirs[package_name] = Path(base_dir)

        if excluded is None:
            excluded = []

        if crawled is None:
            crawled = []

        if not isinstance(includes, list):
            includes = [includes]

        if not isinstance(base_dir, Path):
            base_dir = Path(base_dir)

        base_path = root / base_dir

        for include in includes:
            dirs = []
            others = []

            for element in base_path.glob(include):
                if element.is_dir():
                    dirs.append(element.relative_to(base_path))
                else:
                    others.append(element.relative_to(base_path))

            m = re.match('^([^./]+)/\*\*/\*(\..+)?$', include)
            if m:
                # {dir}/**/* will not take the root directory
                # So we add it
                dirs.insert(0, Path(m.group(1)))

            for dir in dirs:
                if dir in crawled:
                    continue

                package = '.'.join(dir.parts)

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

                    crawled += [base_path / child for child in children]

                crawled.append(real_dir)

            for element in others:
                if base_path / element in crawled or element.suffix == '.pyc':
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

                        crawled.append(base_path / dir)

                crawled.append(base_path / element)

        packages = [p for p in packages if p not in excluded]
        modules = [m for m in modules if m not in excluded]

        settings = {
            'packages': packages,
            'modules': modules
        }

        if package_dirs:
            settings['package_dirs'] = package_dirs

        return settings

    def _ext_modules(self, poet):
        """
        Builds the extension modules.
        
        Transforms the extensions section:
        
        [extensions]
        "my.module" = "my/module.c"
        
        to a proper extension:
        
        Extension('my.module', 'my/module.c')
        
        :param poet: The Poet instance for which to build.
        :type poet: poet.poet.Poet
        
        :rtype: dict 
        """
        extensions = []
        for module, source in poet.extensions.items():
            if not isinstance(source, list):
                source = [source]

            extensions.append(Extension(module, source))

        return {
            'ext_modules': extensions
        }

    def _write_setup(self, setup, dest):
        parameters = setup.copy()

        for key in parameters.keys():
            value = parameters[key]

            if value is not None and not isinstance(value, (list, dict)):
                parameters[key] = repr(value)

        setup_template = template('setup.py')
        with open(dest, 'w') as f:
            f.write(setup_template.render(**parameters))

    def _write_manifest(self, manifest):
        with open(manifest, 'w') as f:
            f.writelines(self._manifest)

    def _write_readme(self, readme, content):
        with open(readme, 'w') as f:
            f.write(content)

