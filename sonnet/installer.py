# -*- coding: utf-8 -*-

import tempfile
import shutil
import zipfile
import toml

import os
import glob

from hashlib import sha256
from pip.commands import InstallCommand, DownloadCommand


class Installer(object):

    def __init__(self, command, repository):
        self._command = command
        self._repository = repository

    def install(self, sonnet, dev=True):
        if not sonnet.is_lock():
            self.lock(sonnet, dev=dev)

            return self.install(sonnet.lock, dev=dev)

        self._command.line('')
        self._command.line('<info>Installing dependencies</>')
        self._command.line('')

        command = InstallCommand()
        for dep in sonnet.dependencies:
            name = dep.name

            if dep.is_vcs_dependency():
                constraint = dep.pretty_constraint
            else:
                constraint = dep.normalized_constraint.replace('==', '')

            self._command.line('  - Installing <info>{}</> (<comment>{}</>)'.format(name, constraint))
            args = [name, '-q']

            command.main(args)

    def lock(self, sonnet, dev=True):
        if sonnet.is_lock():
            return

        self._command.line('')
        self._command.line('<info>Locking dependencies to <comment>sonnet.lock</></>')
        self._command.line('')
        deps = sonnet.pip_dependencies

        if dev:
            deps += sonnet.pip_dev_dependencies

        command = DownloadCommand()

        dir = tempfile.mkdtemp(prefix='sonnet_')

        packages = {}

        for dep in deps:
            self._command.write('  - Locking <info>{}</>'.format(dep.name))

            command.main(['{}'.format(dep.normalized_name), '--dest={}'.format(dir), '-q'])

            # Searching for package and getting information
            package = self.search_package(dir, dep.name)
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
                    archive = zipfile.ZipFile(package['path'])
                    revision = archive.read(
                        '{}/.git/refs/heads/{}'.format(
                            package['name'],
                            dep.constraint['branch']
                        )
                    ).strip().decode()
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

        for package in glob.glob(os.path.join(dir, '*')):
            package = self.get_package(package, existing=packages)
            packages[package['name']] = package

        shutil.rmtree(dir)

        self._write_lock(sonnet, [packages[k] for k in sorted(list(packages.keys()))])

    def search_package(self, dir, package):
        package = self._repository.package_name(package)
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

    def _write_lock(self, sonnet, packages):
        output = {
            'root': {
                'name': sonnet.name,
                'version': sonnet.version
            },
            'package': []
        }

        for package in packages:
            output['package'].append({
                'name': package['name'],
                'version': package['version'],
                'checksum': package['checksum']
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
