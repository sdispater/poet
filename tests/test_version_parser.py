# -*- coding: utf-8 -*-

from semantic_version import Spec
from poet.version_parser import VersionParser


def test_parse_constraints():
    parser = VersionParser()

    assert Spec('>=1.2.3,<2') == parser.parse_constraints('>=1.2.3,<2')
    assert Spec('>=1.2.3,<2') == parser.parse_constraints('>=1.2.3, <2')
    assert Spec('>=1.2.3,<2') == parser.parse_constraints(['>=1.2.3','<2'])

def test_parse_stability():
    assert 'stable' == VersionParser.parse_stability('1.2.3')
    assert 'dev' == VersionParser.parse_stability('1.2.3b1')
