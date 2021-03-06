'''Unit test-style testcases for rdflib_validation.

This should hopefully double as a useful document describing exactly what
errors rdflib_validation checks for.

Test cases that are trying to trigger specific bugs in the code belong in the
test_complex file.

'''


import pytest
import rdflib

import rdflib_validation
from rdflib_validation import (
    DisjointClassMembership, DomainMismatch, RangeMismatch)

from base import ValidationTestCase


# This is boilerplate that gets prepended to every test case before parsing.
STANDARD_PREFIXES = '''
@prefix : <http://example.com/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

'''


class TestObjectProperties(ValidationTestCase):
    '''Tests for validation of property statements between two resources.'''

    SCHEMA = '''
    :ClassA a owl:Class .
    :ClassB a owl:Class .

    :relatedTo a owl:ObjectProperty ;
        rdfs:comment """
            A relationship which can only apply in one direction.

            Imagine a :livesIn property between a person and a building.
            You might live in a house, but the house cannot live in you.
        """ ;
        rdfs:domain :ClassA ;
        rdfs:range :ClassB .

    :instanceA1 a :ClassA .
    :instanceB1 a :ClassB.
    '''

    TESTCASES = {
        ''':instanceA1 :relatedTo :instanceA1 .''':
            [RangeMismatch],
        ''':instanceA1 :relatedTo :instanceB1 .''':
            [DomainMismatch],
        ''':instanceA1 :relatedTo :instanceB1 .''':
            []
    }

    @pytest.mark.parametrize("data,expected", TESTCASES.items())
    def test_all(self, data, expected):
        # FIXME: parsing the schema each time is dumb. Use a fixture.
        data_graph = rdflib.Graph()
        data_graph.parse(data=STANDARD_PREFIXES + data, format='turtle')

        schema_graph = rdflib.Graph()
        schema_graph.parse(data=STANDARD_PREFIXES + self.SCHEMA, format='turtle')

        results = rdflib_validation.validate(data_graph, schema_graph)

        results_classes = set(type(x) for x in results)
        self.assert_result(data, results_classes, expected)


class TestDatatypeProperties(object):
    '''Tests for validation of property statements which specify a datatype.'''

    # FIXME: write them


class TestDisjointClasses(object):
    '''Tests for validation of classes which are 'disjoint' with each other.'''

    SCHEMA = STANDARD_PREFIXES + '''
    : rdfs:comment """
        Two classes where membership of one prevents membership of the other.

        Comparable to :Cat and :Dog classes, for example.
    """

    :classA a owl:Class ;
        owl:disjointWith :classB .

    :classB a owl:Class ;
        owl:disjointWith :classA .
    '''

    TESTCASES = {
        ''':instance a :classA, :classB.''':
            [DisjointClassMembership],
        ''':instance a :classA.''':
            [],
        # Test classes that should be implicitly disjoint as well.
        # FIXME: test that these are indeed invalid statements, using the
        # Apache Jena owlReasoner.validate() code.
        ''':instance a :classA, xsd:integer.''':
            [DisjointClassMembership],
        ''':instance a :classA, xsd:integer.''':
            [DisjointClassMembership],
    }


class TestCardinality(object):
    '''Tests for validation of multiple statements of a given property.'''

    # FIXME: write them
