# Change Log


## [Unreleased]

### Added

- `poet` now uses its own configuration file (used only to store remote repositories for now).

### Changed

- Improved the `publish` command.


## [0.4.1] - 2017-04-26

### Fixed

- Fixes `init` command raising an error when setting dependencies interactively.
- Fixes `make:requirements` command raising an error.


## [0.4.0] - 2017-04-25

### Added

- Added support for Python version restricted dependencies: `pathlib2 = { version = "^2.2", python = "~2.7" }`
- Added ability to create a default template in the `init` command.
- Added a new way to declare the `include` section to reproduce the setup `package_dir` feature.

### Changed

- Improved CLI to display visual clues when actions are being performed (spinner).
- Improved `update` command by removing no longer necessary packages.
- Improved template for the `init` command.

### Fixed

- Fixed `install` command not properly installing packages.


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


[Unreleased]: https://github.com/sdispater/ppoet/compare/0.4.1...master
[0.4.1]: https://github.com/sdispater/poet/releases/tag/0.4.1
[0.4.0]: https://github.com/sdispater/poet/releases/tag/0.4.0
[0.3.2]: https://github.com/sdispater/poet/releases/tag/0.3.2
[0.3.1]: https://github.com/sdispater/poet/releases/tag/0.3.1
[0.3.0]: https://github.com/sdispater/poet/releases/tag/0.3.0
