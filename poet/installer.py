# -*- coding: utf-8 -*-

import tempfile
import zipfile
import subprocess
import toml

import os
import glob
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

            with open(os.devnull) as devnull:
                try:
                    subprocess.check_output([self._command.pip(), 'install', dep.normalized_name], stderr=devnull)
                except subprocess.CalledProcessError as e:
                    self._command.error('Error while installing [{}] ({})'.format(name, str(e)))
                    break

    def lock(self, poet, dev=True):
        if poet.is_lock():
            return

        self._command.line('')
        self._command.line('<info>Locking dependencies to <comment>poetry.lock</></>')
        self._command.line('')

        deps = poet.pip_dependencies
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

        self._command.line('  - <info>Writing dependencies</>')
        self._write_lock(poet, sorted(packages, key=lambda p: p['name'].lower()))

    def _get_vcs_version(self, url, rev):
        tmp_dir = tempfile.mkdtemp()
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

        return version

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
