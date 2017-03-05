# -*- coding: utf-8 -*-

import tempfile
import shutil
import zipfile
import subprocess
import toml

import os
import glob

from hashlib import sha256
from pip.commands import InstallCommand, DownloadCommand


class Installer(object):

    def __init__(self, command, repository):
        self._command = command
        self._repository = repository

    def install(self, poet, dev=True):
        if not poet.is_lock():
            self.lock(poet, dev=dev)

            return self.install(poet.lock, dev=dev)

        self._command.line('')
        self._command.line('<info>Installing dependencies</>')
        self._command.line('')

        command = InstallCommand()

        deps = poet.pip_dependencies

        if dev:
            deps += poet.pip_dev_dependencies

        for dep in deps:
            name = dep.name

            if dep.is_vcs_dependency():
                constraint = dep.pretty_constraint
            else:
                constraint = dep.normalized_constraint.replace('==', '')

            self._command.line('  - Installing <info>{}</> (<comment>{}</>)'.format(name, constraint))
            args = [name]
            if self._command.virtual_env:
                args.append('--target={}'.format(self._command.virtual_env))

            args.append('-q')

            command.main(args)

    def lock(self, poet, dev=True):
        if poet.is_lock():
            return

        self._command.line('')
        self._command.line('<info>Locking dependencies to <comment>poetry.lock</></>')
        self._command.line('')
        deps = poet.pip_dependencies

        dest = tempfile.mkdtemp(prefix='poet_')

        try:
            packages = {}

            self._lock_dependencies(packages, deps, dest)

            if dev:
                # Emptying dir before checking dev dependencies
                for filename in os.listdir(dest):
                    filepath = os.path.join(dest, filename)

                    if os.path.isfile(filepath):
                        os.unlink(filepath)

                self._lock_dependencies(
                    packages,
                    poet.pip_dev_dependencies, dest,
                    category='dev'
                )
        except Exception:
            raise
        finally:
            shutil.rmtree(dest)

        self._write_lock(poet, [packages[k] for k in sorted(list(packages.keys()))])

    def _lock_dependencies(self, packages, deps, dest, category='default'):
        command = DownloadCommand()

        for dep in deps:
            self._command.write('  - Locking <info>{}</>'.format(dep.name))

            command.main(['{}'.format(dep.normalized_name), '--dest={}'.format(dest), '-q'])

            # Searching for package and getting information
            package = self.search_package(dest, dep)
            version_output = package['version']

            if dep.is_vcs_dependency():
                # Retrieving revision to locked to
                vcs_kind = 'rev'
                if 'rev' in dep.constraint:
                    vcs_kind = 'rev'
                    version = dep.constraint['rev']
                elif 'tag' in dep.constraint:
                    vcs_kind = 'tag'
                    version = dep.constraint['tag']
                else:
                    # A branch has been specified
                    # so we have to find the revision to lock to
                    src_dir = tempfile.mkdtemp(prefix='poet_{}_'.format(package['name']))

                    archive = zipfile.ZipFile(package['path'])
                    archive.extractall(src_dir)

                    os.chdir(os.path.join(src_dir, package['name']))
                    subprocess.check_output(['git', 'checkout', dep.constraint['branch']])

                    revision = subprocess.check_output(['git', 'rev-parse', dep.constraint['branch']])
                    revision = revision.decode().strip()
                    version = revision

                version_output = '{} {}'.format(vcs_kind, version)
                package['version'] = {
                    'git': dep.constraint['git'],
                    vcs_kind: version
                }

            self._command.overwrite(
                '  - Locked <info>{}</> to <comment>{}</>\n'.format(
                    dep.name, version_output
                )
            )

            packages[package['name']] = package

        for package in glob.glob(os.path.join(dest, '*')):
            package = self.get_package(package, existing=packages)

            if package['name'] in packages and packages[package['name']]['version'] != package['version']:
                # We found conflicting versions
                raise Exception('Conflict for package [{}]'.format(package['name']))

            if 'category' not in packages:
                package['category'] = category

            packages[package['name']] = package

    def search_package(self, dir, dependency):
        package = self._repository.package_name(dependency.name)
        packages = glob.glob(os.path.join(dir, '{}*'.format(package)))

        if not packages:
            raise Exception('No package [{}] found in {}'.format(package, dir))

        return self.get_package(packages[0])

    @classmethod
    def get_package(cls, package, no_hash=False, existing=None):
        name = os.path.basename(package)
        basename, ext = os.path.splitext(name)
        package_name = name.split('-')[0]

        if existing and package_name in existing:
            return existing[package_name]

        if ext == '.whl':
            basename = '-'.join(basename.split('-')[:-3])

        if basename.endswith('.tar'):
            basename, _ = os.path.splitext(basename)

        # Substring out package name (plus dash) from file name to get version.
        version = basename[len(package_name) + 1:]

        if not no_hash:
            _hash = cls._hash(package)
        else:
            _hash = ''

        return {
            'name': package_name,
            'version': version,
            'checksum': _hash,
            'path': package
        }

    def _write_lock(self, poet, packages):
        output = {
            'root': {
                'name': poet.name,
                'version': poet.version
            },
            'package': []
        }

        for package in packages:
            output['package'].append({
                'name': package['name'],
                'version': package['version'],
                'checksum': package['checksum'],
                'category': package['category']
            })

        with open(self._command.lock_file, 'w') as f:
            f.write(toml.dumps(output))

    @classmethod
    def _hash(cls, filename):
        _hash = sha256()

        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break

                _hash.update(chunk)

        return _hash.hexdigest()
