# -*- coding: utf-8 -*-

from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter

from ...version_selector import VersionSelector
from ...version_parser import VersionParser
from ...utils.lexers import TOMLLexer

from .index_command import IndexCommand


class RequireCommand(IndexCommand):
    """
    Add a dependency to the project.

    require
        {name* : Packages to add}
        {--dev : Packages should be added to dev-dependencies section}
        {--no-install : Do not install packages immediately}
    """

    def handle(self):
        packages = self.argument('name')
        is_dev = self.option('dev')
        install = not self.option('no-install')

        requires = []
        version_parser = VersionParser()

        packages = version_parser.parse_name_version_pairs(packages)

        for package in packages:
            package, constraint = package['name'], package['version']

            matches = self._repository.search(package, 1)

            if not matches:
                self.line('<error>Unable to find package [{}]</>'.format(package))
                package = False
            else:
                exact_match = None
                choices = []

                for found_package in matches:
                    choices.append(found_package['name'])

                    if found_package['name'] == package:
                        exact_match = True
                        break

                if not exact_match:
                    self.line(
                        'Found <info>{}</info> packages matching <info>{}</info>'
                        .format(
                            len(matches),
                            package
                        )
                    )

                    package = self.choice(
                        '\nEnter package # to add, or the complete package name if it is not listed: ',
                        choices,
                        attempts=3
                    )

            # no constraint yet, determine the best version automatically
            if constraint == '*':
                self.line('')
                constraint = self._find_best_version_for_package(package)

                self.line(
                    'Using version <info>{}</info> for <info>{}</info>'
                    .format(constraint, package)
                )

            package += ' {}'.format(constraint)

            if package is not False:
                requires.append(package)

        if requires:
            self.line('')
            section = '[dependencies]'
            if is_dev:
                section = '[dev-dependencies]'

            new_content = None
            with open(self.poet_file) as f:
                # Trying to figure out where
                # to put our new dependencies
                content = f.read().split('\n')
                in_section = False
                index = None
                for i, line in enumerate(content):
                    line = line.strip()

                    if line == section:
                        in_section = True
                        continue

                    if in_section and not line:
                        index = i
                        break

                if index is not None:
                    for i, require in enumerate(requires):
                        content.insert(index + i, '{} = "{}"'.format(*require.split(' ')))

                    new_content = '\n'.join(content)

            if new_content is not None:
                with open(self.poet_file, 'w') as f:
                    f.write(new_content)

                if install:
                    arguments = [
                        ('packages', [r.split(' ')[0] for r in requires])
                    ]

                    self.call('update', arguments)
            else:
                self.line('<warning>Unable to automatically add requirements</warning>')
                self.line('<comment>Add the following lines to the <info>{}</> section</>\n'.format(section))
                for require in requires:
                    line = highlight(
                        '{} = "{}"'.format(*require.split(' ')),
                        TOMLLexer(),
                        TerminalFormatter()
                    )
                    self.write(line)

                self.line('')

    def _find_best_version_for_package(self, package):
        selector = VersionSelector(self._repository)
        package = selector.find_best_candidate(package)

        return selector.find_recommended_require_version(package)
