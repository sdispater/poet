# Poet

Poet helps you declare, manage and install dependencies of Python projects, ensuring you have the right stack everywhere.

The package is **highly experimental** at the moment so expect things to change and break. However, if you feel adventurous
I'd gladly appreciate feedback and pull requests.


## Introduction

`poet` is a tool to handle dependencies installation, building and packaging of Python packages.
It only needs one file to do all of that: `poetry.toml`.

```toml
[package]
name = "pypoet"
version = "0.1.0"
description = "Poet helps you declare, manage and install dependencies of Python projects, ensuring you have the right stack everywhere."

license = "MIT"

authors = [
    "Sébastien Eustace <sebastien@eustace.io>"
]

readme = 'README.md'

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
wheel = "^0.29"
pip-tools = "^1.8.2"
cleo = { git = "https://github.com/sdispater/cleo.git", branch = "master" }

[dev-dependencies]
pytest = "^3.0"
pytest-cov = "^2.4"
coverage = "<4.0"
httpretty = "^0.8.14"

[scripts]
poet = 'poet:app.run'
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


### init

This command will help you create a `poetry.toml` file interactively
by prompting you to provide basic information about your package.

It will interactively ask you to fill in the fields, while using some smart defaults.

```bash
poet init
```

#### Options

   * `--name`: Name of the package. 
   * `--description`: Description of the package.
   * `--author`: Author of the package.
   * `--require`: Package to require with a version constraint. Should be in format `foo:1.0.0`.
   * `--require-dev`: Development requirements, see `--require`.
   * `--index`: Index to use when searching for packages.


### install

The `install` command reads the `poetry.toml` file from the current directory, resolves the dependencies,
and installs them.

```bash
poet install
```

If there is a `poetry.lock` file in the current directory,
it will use the exact versions from there instead of resolving them.
This ensures that everyone using the library will get the same versions of the dependencies.

If there is no `poetry.lock` file, Poet will create one after dependency resolution.


### update

In order to get the latest versions of the dependencies and to update the `poetry.lock` file,
you should use the `update` command.

```bash
poet update
```

This will resolve all dependencies of the project and write the exact versions into `poetry.lock`.

If you just want to update a few packages and not all, you can list them as such:

```bash
poet update requests toml
```

### check

The `check` command will check if the `poetry.toml` file is valid.

```bash
poet check
```


### package

The `package` command builds the source and wheels archives.


### publish

This command builds (if not already built) and publishes the package to the remote repository.
