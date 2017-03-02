Sonnet
======

Sonnet helps you declare, manage and install dependencies of PHP projects, ensuring you have the right stack everywhere.


Introduction
------------

``sonnet`` is a tool to handle dependencies installation, building and packaging of Python packages.
It only needs one file to do all of that, ``sonnet.toml``, which would look like that in its basic form.

.. code-block:: toml

    [package]
    name = "sonnet"
    version = "0.1.0"
    description = "Sonnet helps you declare, manage and install dependencies of PHP projects, ensuring you have the right stack everywhere."
    authors = [
        "Sébastien Eustace <sebastien@eustace.io>"
    ]
    license = "MIT"

    readme = 'README.md'

    repository = "https://github.com/sdispater/pendulum"
    homepage = "https://pendulum.eustace.io"
    documentation = "https://pendulum.eustace.io/docs"

    keywords = ['datetime', 'date', 'time']

    include = ['pendulum/**/*.py']

    python = ["~2.7", "^3.2"]



    [dependencies]
    "regebro/tzlocal" = "^1.3"
    "dateutil/dateutil" = "^2.6"
    "sdispater/pytzdata" = ">=2016.10"

    [dev-dependencies]
    "pytest-dev/pytest" = "^3.0"


    [scripts]
    sonnet = "application.run"


There are some things we can notice here:

* It will try to enforce `semantic versioning <http://semver.org>`_ as the best practice in version naming.
* You can specify the readme, included and excluded files: no more ``MANIFEST.in``.
``sonnet`` will also use VCS ignore files (like ``.gitignore``) to populate the ``exclude`` section.
* Keywords (up to 5) can be specified and will act as tags on the packaging site.
* The dependencies sections support caret, tilde, wildcard, inequality and multiple requirements.
* You must specify the python versions for which your package is compatible.


Commands
--------


``poet init``
~~~~~~~~~~~~~

This command will help you create a ``sonnet.toml`` file interactively
by prompting you to provide basic information about your package:


``poet install``
~~~~~~~~~~~~~~~~

This command will install dependencies specified in ``sonnet.toml`` (or ``sonnet.lock`` if it exists)
and lock them in the ``toml.lock`` file.


``poet check``
~~~~~~~~~~~~~~

This command will check if the ``sonnet.toml`` file is valid.


``poet publish``
~~~~~~~~~~~~~~~~

This command build and publishes the package to the remote repository.
