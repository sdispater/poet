# -*- coding: utf-8 -*-

import os
import re

from collections import OrderedDict
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter

from .index_command import IndexCommand
from ...version_parser import VersionParser
from ...version_selector import VersionSelector
from ...utils.lexers import TOMLLexer
from ...utils.helpers import call, template
from ...build import Builder


class InitCommand(IndexCommand):
    """
    Creates a basic <comment>poetry.toml</> file in current directory.

    init
        { template? : Template to use }
        {--name= : Name of the package}
        {--description= : Description of the package}
        {--author= : Author name of the package}
        {--dependency=* : Package to require with a version constraint,
                          e.g. requests:^2.10.0 or requests==2.11.1}
        {--dev-dependency=* : Package to require for development with a version constraint,
                              e.g. requests:^2.10.0 or requests==2.11.1}
        {--l|license= : License of the package}
    """

    help = """
The <info>init</info> command creates a basic <comment>poetry.toml</> file
in the current directory.

<info>poet init</info>
"""

    def __init__(self):
        self._git_config = None

        super(InitCommand, self).__init__()

    def handle(self):
        formatter = self.get_helper('formatter')

        self.line([
            '',
            formatter.format_block('Welcome to the Poet config generator', 'bg=blue;fg=white', True),
            ''
        ])

        template_name = self.argument('template')
        if template_name:
            self.line([
                '',
                'Using <comment>{}</> template to create '
                'your <info>poetry.toml</> config.'.format(template_name),
                ''
            ])

            if template_name == 'default':
                output = template('poetry.toml').render()

                with open(self.poet_file, 'w') as fd:
                    fd.write(output)

            return

        self.line([
            '',
            'This command will guide you through creating your <info>poetry.toml</> config.',
            ''
        ])

        poet_file = self.poet_file
        git_config = self.git_config()

        name = self.option('name')
        if not name:
            name = os.path.basename(os.path.dirname(poet_file))
            name = name.lower()

        question = self.create_question(
            'Package name [<comment>{}</comment>]: '
            .format(name),
            default=name
        )
        name = self.ask(question)

        version = '0.1.0'
        question = self.create_question(
            'Version [<comment>{}</comment>]: '.format(version),
            default=version
        )
        version = self.ask(question)

        description = self.option('description') or ''
        question = self.create_question(
            'Description [<comment>{}</comment>]: '
                .format(description),
            default=description
        )
        description = self.ask(question)

        author = self.option('author')

        if not author and git_config.get('user.name') and git_config.get('user.email'):
            author = '{} <{}>'.format(git_config['user.name'], git_config['user.email'])

        question = self.create_question(
            'Author [<comment>{}</comment>, n to skip]: '
                .format(author),
            default=author
        )
        question.validator = lambda v: self._validate_author(v, author)

        author = self.ask(question)

        if not author:
            authors = []
        else:
            authors = [author]

        license = self.option('license') or ''

        question = self.create_question(
            'License [<comment>{}</comment>]: '
                .format(license),
            default=license
        )

        license = self.ask(question)

        self.line('')

        requirements = []

        question = 'Would you like to define your dependencies' \
                   ' (require) interactively?'
        if self.confirm(question, True):
            requirements = self._format_requirements(
                self._determine_requirements(self.option('dependency'))
            )

        dev_requirements = []

        question = '<question>Would you like to define your dev dependencies' \
                   ' (require-dev) interactively'
        if self.confirm(question, True):
            dev_requirements = self._format_requirements(
                self._determine_requirements(self.option('dev-dependency'))
            )

        output = template('poetry.toml.jinja2').render(
            name=name,
            version=version,
            description=description,
            authors=authors,
            license=license,
            dependencies=requirements,
            dev_dependencies=dev_requirements
        )

        if self.input.is_interactive():
            self.line('<info>Generated file</>')
            if self.output.is_decorated():
                self.line([
                    '',
                    highlight(
                        output,
                        TOMLLexer(),
                        TerminalFormatter()
                    ),
                    ''
                ])
            else:
                self.line(['', output, ''])

            if not self.confirm(
                'Do you confirm generation?', True
            ):
                self.line('<error>Command aborted</error>')

                return 1

            with open(self.poet_file, 'w') as fd:
                fd.write(output)

    def _determine_requirements(self, requires):
        if requires:
            requires = self._normalize_requirements(requires)
            result = []

            for requirement in requires:
                if 'version' not in requirement:
                    # determine the best version automatically
                    version = self._find_best_version_for_package(requirement['name'])
                    requirement['version'] = version

                    self.line(
                        'Using version <info>{}</info> for <info{}</info>'
                        .format(requirement['version'], requirement['name'])
                    )

                result.append(requirement['name'] + ' ' + requirement['version'])

        version_parser = VersionParser()
        question = self.create_question('Search for a package:')
        package = self.ask(question)
        while package is not None:
            matches = self._find_packages(package)

            if not matches:
                self.line('<error>Unable to find package</>')
                package = False
            else:
                exact_match = None
                choices = []

                for found_package in matches:
                    choices.append(found_package['name'])

                    # Removing exact match feature for now
                    # if found_package['name'] == package:
                    #     exact_match = True
                    #     break

                if not exact_match:
                    self.line(
                        'Found <info>{}</info> packages matching <info>{}</info>'
                        .format(
                            len(matches),
                            package
                        )
                    )

                    package = self.choice(
                        '\nEnter package # to add, or the complete package name if it is not listed',
                        choices,
                        attempts=3
                    )

            # no constraint yet, determine the best version automatically
            if package is not False and ' ' not in package:
                question = self.create_question(
                    'Enter the version constraint to require '
                    '(or leave blank to use the latest version):'
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

            package = self.ask('\nSearch for a package:')

        return requires

    def _validate_author(self, author, default):
        author = author or default

        if author in ['n', 'no']:
            return

        m = Builder.AUTHOR_REGEX.match(author)
        if not m:
            raise ValueError(
                'Invalid author string. Must be in the format: '
                'John Smith <john@example.com>'
            )

        return author

    def _find_packages(self, package):
        return self._repository.search(package, 1)

    def _find_best_version_for_package(self, package):
        selector = VersionSelector(self._repository)
        package = selector.find_best_candidate(package)

        return selector.find_recommended_require_version(package)

    def _format_requirements(self, requirements):
        requires = OrderedDict()
        requirements = self._normalize_requirements(requirements)

        for requirement in requirements:
            requires[requirement['name']] = requirement['version']

        return requires

    def _normalize_requirements(self, requirements):
        parser = VersionParser()

        return parser.parse_name_version_pairs(requirements)

    def git_config(self):
        config_list = call(['git', 'config', '-l'])

        git_config = {}

        m = re.findall('(?ms)^([^=]+)=(.*?)$', config_list)
        if m:
            for group in m:
                git_config[group[0]] = group[1]

        return git_config
