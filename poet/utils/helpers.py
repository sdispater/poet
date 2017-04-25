# -*- coding: utf-8 -*-

import subprocess

from jinja2 import Environment, PackageLoader

from .._compat import decode, PY3K


TEMPLATE_ENV = Environment(
    loader=PackageLoader('poet', 'templates'),
    autoescape=False,
    lstrip_blocks=True,
    trim_blocks=True
)

TEMPLATE_ENV.globals.update({
    'isinstance': isinstance,
    'list': list,
    'sorted': sorted,
    'repr': repr
})


def call(args):
    """
    Calls a command and return the output.
    
    :param args: The command args.
    :type args: list
    
    :rtype: str 
    """
    output = subprocess.check_output(args, stderr=subprocess.STDOUT)

    if PY3K:
        return decode(output)

    return output


def template(name):
    """
    Returns a template given a name.
    
    :param name: The name of the template.
    :type name: str
    
    :rtype: jinja2.Template 
    """
    if not name.endswith('.jinja2'):
        name += '.jinja2'

    return TEMPLATE_ENV.get_template(name)
