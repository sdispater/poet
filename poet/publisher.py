# -*- coding: utf-8 -*-

import os
import twine.utils
import toml

from twine.commands.upload import find_dists, skip_upload
from twine.repository import Repository as BaseRepository
from twine.exceptions import PackageNotFound, RedirectDetected
from twine.package import PackageFile
from requests_toolbelt.multipart import (
    MultipartEncoder, MultipartEncoderMonitor
)

from .locations import CONFIG_DIR
from .utils.helpers import template, mkdir_p


class Repository(BaseRepository):

    def __init__(self, output, repository_url, username, password):
        self._output = output

        super(Repository, self).__init__(repository_url, username, password)

    def register(self, package):
        data = package.metadata_dictionary()
        data.update({
            ":action": "submit",
            "protocol_version": "1",
        })

        self._output.writeln(
            " - Registering <info>{0}</>".format(package.basefilename)
        )

        data_to_send = self._convert_data_to_list_of_tuples(data)
        encoder = MultipartEncoder(data_to_send)
        resp = self.session.post(
            self.url,
            data=encoder,
            allow_redirects=False,
            headers={'Content-Type': encoder.content_type},
        )
        # Bug 28. Try to silence a ResourceWarning by releasing the socket.
        resp.close()

        return resp

    def _upload(self, package):
        data = package.metadata_dictionary()
        data.update({
            # action
            ":action": "file_upload",
            "protocol_version": "1",
        })

        data_to_send = self._convert_data_to_list_of_tuples(data)

        with open(package.filename, "rb") as fp:
            data_to_send.append((
                "content",
                (package.basefilename, fp, "application/octet-stream"),
            ))
            encoder = MultipartEncoder(data_to_send)
            bar = self._output.create_progress_bar(encoder.len)
            bar.set_format(
                " - Uploading <info>{0}</> <comment>%percent%%</>".format(package.basefilename)
            )
            monitor = MultipartEncoderMonitor(
                encoder, lambda monitor: bar.set_progress(monitor.bytes_read / encoder.len)
            )

            bar.start()

            resp = self.session.post(
                self.url,
                data=monitor,
                allow_redirects=False,
                headers={'Content-Type': monitor.content_type},
            )

            if resp.ok:
                bar.finish()

                self._output.writeln('')
            else:
                self._output.overwrite('')

        return resp


class Publisher(object):
    """
    Registers and publishes packages to remote repositories.
    """

    def __init__(self, output, repository_name=None,
                 username=None, password=None,
                 cert=None, client_cert=None, repository_url=None):
        self._output = output
        self._repository_config = None

        if not repository_name and not repository_url:
            raise Exception('Either a repository name or a repository url should be provided.')

        if not repository_url:
            config_file = os.path.join(CONFIG_DIR, 'config.toml')
            if not os.path.exists(config_file):
                self._create_config_file()

            with open(config_file) as f:
                config = toml.loads(f.read())

            for repo in config['repository']:
                if repo['name'] == repository_name:
                    self._repository_config = repo
                    break
        else:
            self._repository_config = {
                'url': repository_url
            }

        if not self._repository_config:
            raise Exception('Repository [{}] does not exist.'.format(repository_name))

        self._repository_config['url'] = twine.utils.normalize_repository_url(
            self._repository_config['url']
        )

        username = self._repository_config.get('username')
        if not username:
            self._output.writeln('')
            username = self._output.ask('Enter your username:')

        password = self._repository_config.get('password')
        if not password:
            self._output.writeln('')
            password = self._output.ask_hidden('Enter your password:')

        ca_cert = cert
        if not ca_cert:
            ca_cert = self._repository_config.get('ca_cert')

        if not client_cert:
            client_cert = self._repository_config.get('client_cert')

        self._repository = Repository(
            output, self._repository_config['url'], username, password
        )
        self._repository.set_certificate_authority(ca_cert)
        self._repository.set_client_certificate(client_cert)

    def register(self, poet):
        """
        Register a package represented by a Poet instance.
        
        :param poet: The Poet instance representing the package.
        :type poet: poet.poet.Poet
        """
        package = os.path.join(poet.base_dir, 'dist', poet.archive)

        if not os.path.exists(package):
            raise PackageNotFound(
                '"{0}" does not exist on the file system.'.format(package)
            )

        resp = self._repository.register(PackageFile.from_filename(package, None))
        self._repository.close()

        if resp.is_redirect:
            raise RedirectDetected(
                ('"{0}" attempted to redirect to "{1}" during registration.'
                 ' Aborting...').format(self._repository.url,
                                        resp.headers["location"]))

        resp.raise_for_status()

    def upload(self, poet):
        """
        Upload packages represented by a Poet instance.

        :param poet: The Poet instance representing the package.
        :type poet: poet.poet.Poet
        """
        skip_existing = False
        dists = find_dists(
            [
                os.path.join(
                    os.path.join(poet.base_dir, 'dist'),
                    '{}-{}*'.format(poet.name, poet.version)
                )
            ]
        )

        uploads = [i for i in dists if not i.endswith(".asc")]

        for filename in uploads:
            package = PackageFile.from_filename(filename, None)
            skip_message = (
                " - Skipping <comment>{0}</> because it appears to already exist"
                .format(
                    package.basefilename
                )
            )

            # Note: The skip_existing check *needs* to be first, because otherwise
            #       we're going to generate extra HTTP requests against a hardcoded
            #       URL for no reason.
            if skip_existing and self._repository.package_is_uploaded(package):
                self._output.writeln(skip_message)
                continue

            resp = self._repository.upload(package)

            # Bug 92. If we get a redirect we should abort because something seems
            # funky. The behaviour is not well defined and redirects being issued
            # by PyPI should never happen in reality. This should catch malicious
            # redirects as well.
            if resp.is_redirect:
                raise RedirectDetected(
                    ('"{0}" attempted to redirect to "{1}" during upload.'
                     ' Aborting...').format(self._repository.url,
                                            resp.headers["location"]))

            if skip_upload(resp, skip_existing, package):
                self._output.writeln(skip_message)

                continue

            twine.utils.check_status_code(resp)

        # Bug 28. Try to silence a ResourceWarning by clearing the connection
        # pool.
        self._repository.close()

    def _create_config_file(self):
        config_file = os.path.join(CONFIG_DIR, 'config.toml')

        mkdir_p(CONFIG_DIR)

        # Try to load default ~/.pypirc file to transfer
        path = os.path.expanduser('~/.pypirc')
        if not os.path.exists(path):
            config = self._get_default_config()
        else:
            pypirc_config = twine.utils.get_config()

            repositories = []
            for repository, settings in pypirc_config.items():
                repositories.append({
                    'name': repository,
                    'url': settings.get('repository', 'https://pypi.python.org/pypi'),
                    'username': settings.get('username'),
                    'password': settings.get('password'),
                })

            config = {
                'repositories': repositories
            }

        with open(config_file, 'w') as f:
            f.write(template('config.toml').render(**config))

    def _get_default_config(self):
        return {
            'repositories': [
                {'name': 'pypi', 'url': 'https://pypi.python.org/pypi'}
            ]
        }

