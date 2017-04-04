# Poet

Poet helps you declare, manage and install dependencies of Python projects, ensuring you have the right stack everywhere.

The package is **highly experimental** at the moment so expect things to change and break. However, if you feel adventurous
I'd gladly appreciate feedback and pull requests.

## Installation

```bash
pip install pypoet
```

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
homepage = "https://github.com/sdispater/poet"

keywords = ['packaging', 'poet']

include = ['poet/**/*', 'LICENSE']

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

## Why?

Packaging system and dependency management in Python is rather convoluted and hard to understand for newcomers.
Even for seasoned developers it might be cumbersome at times to create all files needed in a Python project: `setup.py`,
`requirements.txt`, `setup.cfg`, `MANIFEST.in`.

So I wanted a tool that would limit everything to a single configuration file to do everything: dependency management, packaging
and publishing.

I takes inspiration in tools that exist in other languages, like `composer` (PHP) or `cargo` (Rust).

Note that there is no magic here, `poet` uses existing tools (`pip`, `twine`, `setuptools`, `distutils`, `pip-tools`) under the hood
to achieve that in a more intuitive way.


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

#### Options

* `--no-dev`: Do not install dev dependencies.
* `--index`: The index to use when installing packages.


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

#### Options

* `--index`: The index to use when installing packages.


### package

The `package` command builds the source and wheels archives.

#### Options

* `--no-universal`: Do not build a universal wheel.
* `--no-wheels`: Build only the source package.
*  `-c|--clean`: Make a clean package.

### publish

This command builds (if not already built) and publishes the package to the remote repository.

It will automatically register the package before uploading if this is the first time it is submitted.

#### Options

* `-r|--repository`: The repository to register the package to (default: `pypi`). Should match a section of your `~/.pypirc` file.

### check

The `check` command will check if the `poetry.toml` file is valid.

```bash
poet check
```


## The `poetry.toml` file

A `poetry.toml` file is composed of multiple sections.

### package

This section describes the specifics of the package

#### name

The name of the package. **Required**

#### version

The version of the package. **Required**

This should follow [semantic versioning](http://semver.org/). However it will not be enforced and you remain
free to follow another specification.

#### description

A short description of the package. **Required**

#### license

The license of the package.

The recommended notation for the most common licenses is (alphabetical):

* Apache-2.0
* BSD-2-Clause
* BSD-3-Clause
* BSD-4-Clause
* GPL-2.0
* GPL-2.0+
* GPL-3.0
* GPL-3.0+
* LGPL-2.1
* LGPL-2.1+
* LGPL-3.0
* LGPL-3.0+
* MIT

Optional, but it is highly recommended to supply this.
More identifiers are listed at the [SPDX Open Source License Registry](https://www.spdx.org/licenses/).

#### authors

The authors of the package. This is a list of authors and should contain at least one author.

Authors must be in the form `name <email>`.

#### readme

The readme file of the package. **Required**

The file can be either `README.rst` or `README.md`.
If it's a markdown file you have to install the [pandoc](https://github.com/jgm/pandoc) utility so that it can be automatically
converted to a RestricturedText file.

#### homepage

An URL to the website of the project. **Optional**

#### repository

An URL to the repository of the project. **Optional**

#### documentation

An URL to the documentation of the project. **Optional**

#### keywords

A list of keywords (max: 5) that the package is related to. **Optional**

#### python

A list of Python versions for which the package is compatible. **Required**

#### include and exclude

A list of patterns that will be included in the final package.

You can explicitly specify to Poet that a set of globs should be ignored or included for the purposes of packaging.
The globs specified in the exclude field identify a set of files that are not included when a package is built.

If a VCS is being used for a package, the exclude field will be seeded with the VCS’ ignore settings (`.gitignore` for git for example).

```toml
[package]
# ...
include = ["package/**/*.py", "package/**/.c"]
```

```toml
exclude = ["package/excluded.py"]
```

### `dependencies` and `dev-dependencies`

Poet is configured to look for dependencies on [PyPi](https://pypi.python.org/pypi) by default.
Only the name and a version string are required in this case.

```toml
[dependencies]
requests = "^2.13.0"
```

#### Caret requirement

**Caret requirements** allow SemVer compatible updates to a specified version.
An update is allowed if the new version number does not modify the left-most non-zero digit in the major, minor, patch grouping.
In this case, if we ran `poet update requests`, poet would update us to version `2.14.0` if it was available,
but would not update us to `3.0.0`.
If instead we had specified the version string as `^0.1.13`, poet would update to `0.1.14` but not `0.2.0`.
`0.0.x` is not considered compatible with any other version.

Here are some more examples of caret requirements and the versions that would be allowed with them:

```text
^1.2.3 := >=1.2.3 <2.0.0
^1.2 := >=1.2.0 <2.0.0
^1 := >=1.0.0 <2.0.0
^0.2.3 := >=0.2.3 <0.3.0
^0.0.3 := >=0.0.3 <0.0.4
^0.0 := >=0.0.0 <0.1.0
^0 := >=0.0.0 <1.0.0
```

#### Tilde requirements

**Tilde requirements** specify a minimal version with some ability to update.
If you specify a major, minor, and patch version or only a major and minor version, only patch-level changes are allowed.
If you only specify a major version, then minor- and patch-level changes are allowed.

`~1.2.3` is an example of a tilde requirement.

```text
~1.2.3 := >=1.2.3 <1.3.0
~1.2 := >=1.2.0 <1.3.0
~1 := >=1.0.0 <2.0.0
```

#### Wildcard requirements

**Wildcard requirements** allow for any version where the wildcard is positioned.

`*`, `1.*` and `1.2.*` are examples of wildcard requirements.

```text
* := >=0.0.0
1.* := >=1.0.0 <2.0.0
1.2.* := >=1.2.0 <1.3.0
```

#### Inequality requirements

**Inequality requirements** allow manually specifying a version range or an exact version to depend on.

Here are some examples of inequality requirements:

```text
>= 1.2.0
> 1
< 2
!= 1.2.3
```

#### Multiple requirements

Multiple version requirements can also be separated with a comma, e.g. `>= 1.2, < 1.5`.

#### `git` dependencies

To depend on a library located in a `git` repository,
the minimum information you need to specify is the location of the repository with the git key:

```toml
[dependencies]
requests = { git = "https://github.com/kennethreitz/requests.git" }
```

Since we haven’t specified any other information, Poet assumes that we intend to use the latest commit on the `master` branch
to build our project.
You can combine the `git` key with the `rev`, `tag`, or `branch` keys to specify something else.
Here's an example of specifying that you want to use the latest commit on a branch named `next`:

```toml
[dependencies]
requests = { git = "https://github.com/kennethreitz/requests.git", branch = "next" }
```

### `scripts`

This section describe the scripts or executable that will be installed when installing the package

```toml
[scripts]
poet = 'poet:app.run'
```

Here, we will have the `poet` script installed which will execute `app.run` in the `poet` package.


## Resources

* [Official Website](https://github.com/sdispater/poet)
* [Issue Tracker](https://github.com/sdispater/poet/issues)
