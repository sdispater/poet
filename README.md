# Poet

Poet helps you declare, manage and install dependencies of Python projects, ensuring you have the right stack everywhere.


## Introduction

`poet` is a tool to handle dependencies installation, building and packaging of Python packages.
It only needs one file to do all of that: `poetry.toml`.

```toml
[package]
name = "poet"
version = "0.1.0"
description = "Poet helps you declare, manage and install dependencies of PHP projects, ensuring you have the right stack everywhere."

license = "MIT"

authors = [
    "Sébastien Eustace <sebastien@eustace.io>"
]

readme = 'README.rst'

repository = "https://github.com/sdispater/poet"
homepage = "https://poet.eustace.io"
documentation = "https://poet.eustace.io/docs"

keywords = ['packaging', 'poet']

include = ['poet/**/*']

python = ["~2.7", "^3.2"]


[dependencies]
toml = "^0.9"
requests = "^2.13"
semantic_version = "^2.6"
pygments = "^2.2"
twine = "^1.8"
cleo = { git = "git+https://github.com/sdispater/cleo.git", branch = "master" }

[dev-dependencies]
pytest = "^3.0"


[scripts]
poet = 'app.run'
```

There are some things we can notice here:

* It will try to enforce [semantic versioning](<http://semver.org>) as the best practice in version naming.
* You can specify the readme, included and excluded files: no more `MANIFEST.in`.
`poet` will also use VCS ignore files (like `.gitignore`) to populate the `exclude` section.
* Keywords (up to 5) can be specified and will act as tags on the packaging site.
* The dependencies sections support caret, tilde, wildcard, inequality and multiple requirements.
* You must specify the python versions for which your package is compatible.


`poet` will also detect if you are inside a virtualenv and install the packages accordingly. So, `poet` can
be installed globally and used everywhere.


## Commands


### `poet init`

This command will help you create a `poetry.toml` file interactively
by prompting you to provide basic information about your package:


### `poet install`

This command will install dependencies specified in `poetry.toml` (or `poetry.lock` if it exists)
and lock them in the `poetry.lock` file.


### `poet check`

This command will check if the `poetry.toml` file is valid.


### `poet publish`

This command build and publishes the package to the remote repository.
