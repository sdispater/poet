# -*- coding: utf-8 -*-

import tempfile
import subprocess
import toml

import os
import shutil

from hashlib import sha256
from pip.download import unpack_url
from pip.index import Link
from piptools.resolver import Resolver
from piptools.repositories import PyPIRepository
from piptools.scripts.compile import get_pip_command
from piptools.cache import DependencyCache
from piptools.utils import is_pinned_requirement

from .locations import CACHE_DIR
from .package.pip_dependency import PipDependency


class Installer(object):

    def __init__(self, command, repository):
        self._command = command
        self._poet = command.poet
        self._repository = repository

    def install(self, dev=True):
        if not os.path.exists(self._poet.lock_file):
            self.lock(dev=dev)

            return self.install(dev=dev)

        self._command.line('')
        self._command.line('<info>Installing dependencies</>')
        self._command.line('')

        lock = self._poet.lock
        deps = lock.pip_dependencies

        if dev:
            deps += lock.pip_dev_dependencies

        for dep in deps:
            name = dep.name

            if dep.is_vcs_dependency():
                constraint = dep.pretty_constraint
            else:
                constraint = dep.normalized_constraint.replace('==', '')

            self._command.line('  - Installing <info>{}</> (<comment>{}</>)'.format(name, constraint))

            with open(os.devnull) as devnull:
                try:
                    subprocess.check_output([self._command.pip(), 'install', dep.normalized_name], stderr=devnull)
                except subprocess.CalledProcessError as e:
                    self._command.error('Error while installing [{}] ({})'.format(name, str(e)))
                    break

    def update(self, dev=True):
        if self._poet.is_lock():
            raise Exception('Update is only available with a poetry.toml file.')

        self._command.line('')
        self._command.line('<info>Updating dependencies</>')
        self._command.line('')

        # Reading current lock
        lock = self._poet.lock
        current_deps = lock.pip_dependencies
        if dev:
            current_deps += lock.pip_dev_dependencies

        # Resolving new dependencies and locking them
        deps = self._poet.pip_dependencies
        if dev:
            deps += self._poet.pip_dev_dependencies

        packages = self._resolve(deps)
        deps = [PipDependency(p['name'], p['version']) for p in packages]

        to_act_on = []
        for i, dep in enumerate(deps):
            action = None
            from_ = None
            found = False
            for j, current_dep in enumerate(current_deps):
                name = dep.name
                current_name = current_dep.name
                version = dep.normalized_constraint
                current_version = current_dep.normalized_constraint

                if name == current_name:
                    found = True

                    if version == current_version:
                        break

                    action = 'update'
                    from_ = current_dep
                    break

            if not found:
                action = 'install'

            if action:
                to_act_on.append((action, from_, dep))

        if not to_act_on:
            self._command.line('  - <info>Dependencies already up-to-date!</info>')

            return

        error = False
        for action, from_, dep in to_act_on:
            cmd = [self._command.pip(), 'install', dep.normalized_name]
            description = 'Installing'
            if action == 'update':
                description = 'Updating'
                cmd.append('-U')

            name = dep.name

            if dep.is_vcs_dependency():
                constraint = dep.pretty_constraint
            else:
                constraint = dep.normalized_constraint.replace('==', '')

            version = '<comment>{}</>'.format(constraint)

            if from_:
                if from_.is_vcs_dependency():
                    constraint = from_.pretty_constraint
                else:
                    constraint = from_.normalized_constraint.replace('==', '')

                version = '<comment>{}</> -> '.format(constraint) + version

            self._command.line('  - {} <info>{}</> ({})'.format(description, name, version))

            with open(os.devnull) as devnull:
                try:
                    subprocess.check_output(cmd, stderr=devnull)
                except subprocess.CalledProcessError as e:
                    error = True
                    self._command.error('Error while installing [{}] ({})'.format(name, str(e)))
                    break

        if not error:
            self._write_lock(packages)

    def lock(self, dev=True):
        if self._poet.is_lock():
            return

        self._command.line('')
        self._command.line('<info>Locking dependencies to <comment>poetry.lock</></>')
        self._command.line('')

        deps = self._poet.pip_dependencies

        if dev:
            deps += self._poet.pip_dev_dependencies

        packages = self._resolve(deps)

        self._write_lock(packages)

    def _resolve(self, deps):
        constraints = [dep.as_requirement() for dep in deps]

        command = get_pip_command()
        opts, _ = command.parse_args([])

        self._command.line('  - <info>Resolving dependencies</>')
        resolver = Resolver(
            constraints, PyPIRepository(opts, command._build_session(opts)),
            cache=DependencyCache(CACHE_DIR)
        )
        matches = resolver.resolve()
        pinned = [m for m in matches if not m.editable and is_pinned_requirement(m)]
        unpinned = [m for m in matches if m.editable or not is_pinned_requirement(m)]
        hashes = resolver.resolve_hashes(pinned)
        packages = []
        for m in matches:
            name = m.req.name
            version = str(m.req.specifier)
            if m in unpinned:
                url, specifier = m.link.url.split('@')
                rev, _ = specifier.split('#')

                version = self._get_vcs_version(url, rev)
                checksum = 'sha1:{}'.format(version['rev'])
            else:
                version = version.replace('==', '')
                checksum = list(hashes[m])

            package = {
                'name': name,
                'version': version,
                'checksum': checksum,
                'category': 'main'
            }

            packages.append(package)

        return sorted(packages, key=lambda p: p['name'].lower())

    def _get_vcs_version(self, url, rev):
        tmp_dir = tempfile.mkdtemp()
        current_dir = self._poet.base_dir

        try:
            unpack_url(Link(url), tmp_dir, download_dir=tmp_dir, only_download=True)

            os.chdir(tmp_dir)
            with open(os.devnull) as devnull:
                subprocess.check_output(['git', 'checkout', rev], stderr=devnull)

                revision = subprocess.check_output(['git', 'rev-parse', rev], stderr=devnull)

            revision = revision.decode().strip()
            version = {
                'git': url,
                'rev': revision
            }
        except Exception:
            raise
        finally:
            shutil.rmtree(tmp_dir)
            # Going back to current directory
            os.chdir(current_dir)

        return version

    def _write_lock(self, packages):
        self._command.line('  - <info>Writing dependencies</>')

        output = {
            'root': {
                'name': self._poet.name,
                'version': self._poet.version
            },
            'package': []
        }

        for package in packages:
            output['package'].append({
                'name': package['name'],
                'version': package['version'],
                'checksum': package.get('checksum'),
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
