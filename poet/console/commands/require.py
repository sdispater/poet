# -*- coding: utf-8 -*-

from ...version_selector import VersionSelector

from .index_command import IndexCommand


class RequireCommand(IndexCommand):
    """
    Add a dependency to the project.

    require
        {name* : Packages to add}
        {--dev : Packages should be added to dev-dependencies section}
        {--install : Install packages immediately}
    """

    def handle(self):
        packages = self.argument('name')
        is_dev = self.option('dev')
        install = self.option('install')
        if install:
            self.line('<warning>--install option is not supported yet.</>')

        requires = []

        for package in packages:
            constraint = None

            if ' ' in package:
                package, constraint = package.split(' ')

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
            if package is not False and ' ' not in package:
                self.line('')
                question = self.create_question(
                    'Enter the version constraint to require for <info>{}</> '
                    '(or leave blank to use the latest version): '
                    .format(package)
                )
                question.attempts = 3
                question.validator = lambda x: (x or '').strip() or False

                constraint = self.ask(question)

                if constraint is False:
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

            self.line('<comment>Add the following lines to the <info>{}</> section</>\n'.format(section))
            for require in requires:
                self.line('{} = "{}"'.format(*require.split(' ')))

    def _find_best_version_for_package(self, package):
        selector = VersionSelector(self._repository)
        package = selector.find_best_candidate(package)

        return selector.find_recommended_require_version(package)
