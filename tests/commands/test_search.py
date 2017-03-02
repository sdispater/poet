# -*- coding: utf-8 -*-

import httpretty

from cleo import CommandTester
from sonnet.console import Application


RESULTS_RESPONSE = """<?xml version='1.0'?>
<methodResponse>
    <params>
        <param>
            <value>
                <array>
                    <data>
                        <value>
                            <struct>
                                <member>
                                    <name>_pypi_ordering</name>
                                    <value>
                                        <boolean>0</boolean>
                                    </value>
                                </member>
                                <member>
                                    <name>version</name>
                                    <value>
                                        <string>0.6.0</string>
                                    </value>
                                </member>
                                <member>
                                    <name>name</name>
                                    <value>
                                        <string>pendulum</string>
                                    </value>
                                </member>
                                <member>
                                    <name>summary</name>
                                    <value>
                                        <string>Python datetimes made easy.</string>
                                    </value>
                                </member>
                            </struct>
                        </value>
                    </data>
                </array>
            </value>
        </param>
    </params>
</methodResponse>"""


@httpretty.activate
def test_search_with_results():
    httpretty.register_uri(
        httpretty.POST, 'https://pypi.python.org/pypi',
        body=RESULTS_RESPONSE,
        content_type='text/xml'
    )

    app = Application()

    command = app.find('search')
    command_tester = CommandTester(command)
    command_tester.execute([
        ('command', command.get_name()),
        ('tokens', ['pendulum'])
    ])

    output = command_tester.get_display()

    assert '\npendulum (0.6.0)\n Python datetimes made easy.\n' == output
