# -*- coding: utf-8 -*-

import os
import twine.utils

from twine.commands.upload import find_dists, skip_upload
from twine.repository import Repository as BaseRepository
from twine.exceptions import PackageNotFound, RedirectDetected
from twine.package import PackageFile
from requests_toolbelt.multipart import (
    MultipartEncoder, MultipartEncoderMonitor
)


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

    def __init__(self, output, repository,
                 username=None, password=None, config_file='~/.pypirc',
                 cert=None, client_cert=None, repository_url=None):
        self._output = output

        config = twine.utils.get_repository_from_config(
            config_file,
            repository,
            repository_url
        )
        config["repository"] = twine.utils.normalize_repository_url(
            config["repository"]
        )

        username = twine.utils.get_username(username, config)
        password = twine.utils.get_password(password, config)
        ca_cert = twine.utils.get_cacert(cert, config)
        client_cert = twine.utils.get_clientcert(client_cert, config)

        self._repository = Repository(
            output, config["repository"], username, password
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
