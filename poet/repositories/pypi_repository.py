# -*- coding: utf-8 -*-

import requests
from pip.models import PyPI

try:
    from xmlrpc.client import ServerProxy
except ImportError:
    from xmlrpclib import ServerProxy

from semantic_version import Version

from ..version_parser import VersionParser
from ..package import Package


class PyPiRepository(object):

    DEFAULT_URL = PyPI.pypi_url

    SEARCH_FULLTEXT = 0
    SEARCH_NAME = 1

    def __init__(self, url=DEFAULT_URL):
        self._url = url

    def find_packages(self, name, constraint=None):
        packages = []

        if constraint is not None:
            version_parser = VersionParser()
            constraint = version_parser.parse_constraints(constraint)

        with ServerProxy(self._url) as client:
            versions = client.package_releases(name, True)

        if constraint:
            versions = constraint.select([Version.coerce(v) for v in versions])

        for version in versions:
            try:
                packages.append(Package(name, version))
            except ValueError:
                continue

        return packages

    def search(self, query, mode=0):
        results = []

        search = {
            'name': query
        }

        if mode == self.SEARCH_FULLTEXT:
            search['summary'] = query

        client = ServerProxy(self._url)
        hits = client.search(search, 'or')

        for hit in hits:
            results.append({
                'name': hit['name'],
                'description': hit['summary'],
                'version': hit['version']
            })

        return results

    def package_name(self, name):
        url = 'https://pypi.python.org/pypi/{}/json'.format(name)

        response = requests.get(url)

        if response.status_code == 404:
            raise Exception('Package [{}] not found'.format(name))

        response.raise_for_status()

        info = response.json()['info']

        return info['name']
