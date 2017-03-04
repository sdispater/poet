# -*- coding: utf-8 -*-


class PoetFileError(Exception):

    pass


class MissingElement(PoetFileError):

    def __init__(self, element):
        super(MissingElement, self).__init__(
            'The poetry.toml file is missing the [{}] element'.format(element)
        )


class InvalidElement(PoetFileError):

    def __init__(self, element, extra_info=''):
        msg = 'The element [{}] is invalid'.format(element)

        if extra_info:
            msg += ' ({})'.format(extra_info)

        super(InvalidElement, self).__init__(msg)
