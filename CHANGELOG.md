# Change Log

## [Unreleased]

### Added

- Added support for Python version restricted dependencies: `pathlib2 = { version = "^2.2", python = "~2.7" }`
- Added ability to create a default template in the `init` command.

### Changed

- Improved `update` command by removing no longer necessary packages.
- Improved template for the `init` command.


## [0.3.2] - 2017-04-13

### Fixed

- Fixed `Builder` not setting `tests_require` in setup file.
- Fixed error in `init` command when accessing git config.


## [0.3.1] - 2017-04-11

### Fixed

- Fixed optional dependencies being set in the `install_requires` section.


## [0.3.0] - 2017-04-11

### Added

- Added support for features.
- Added support for prerelease dependencies.

### Fixed

- Properly resolves dependencies categories.


[Unreleased]: https://github.com/sdispater/ppoet/compare/0.3.2...master
[0.3.2]: https://github.com/sdispater/poet/releases/tag/0.3.2
[0.3.1]: https://github.com/sdispater/poet/releases/tag/0.3.1
[0.3.0]: https://github.com/sdispater/poet/releases/tag/0.3.0
