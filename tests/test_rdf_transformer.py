# tests/test_rdf_transformer.py
import pytest
from rdflib import Graph, URIRef, Literal, Namespace
from strings2things.app.core.rdf_transformer import RDFTransformer

EX = Namespace("http://example.org/ontology#")


@pytest.fixture
def simple_label_map():
    """
    Mock label map: labels -> instance IRIs
    """
    return {
        "geology": str(EX.Geology),
        "biology": str(EX.Biology),
        "physics": str(EX.Physics),
    }


@pytest.fixture
def input_graph_simple():
    g = Graph()
    # Exact match
    g.add((EX.subj1, EX.hasCategory, Literal("geology")))
    # Fuzzy match
    g.add((EX.subj2, EX.hasCategory, Literal("biolgy")))
    # Unknown
    g.add((EX.subj3, EX.hasCategory, Literal("unknownlabel")))
    # Non-literal
    g.add((EX.subj4, EX.hasValue, URIRef("http://example.org/someIRI")))
    return g


def test_rdf_transformer(simple_label_map, input_graph_simple):
    # Use full predicate IRI in the label map
    predicate_label_map = {str(EX.hasCategory): simple_label_map}

    transformer = RDFTransformer(
        predicate_label_map=predicate_label_map,
        fuzzy=True,
        fuzzy_threshold=90
    )
    output_graph = transformer.transform(input_graph_simple)

    # Exact match → replaced with IRI
    assert (EX.subj1, EX.hasCategory, EX.Geology) in output_graph
    # Fuzzy match → replaced with closest IRI
    assert (EX.subj2, EX.hasCategory, EX.Biology) in output_graph
    # Unknown → remains literal
    assert (EX.subj3, EX.hasCategory, Literal("unknownlabel")) in output_graph
    # Non-literal → untouched
    assert (EX.subj4, EX.hasValue, URIRef("http://example.org/someIRI")) in output_graph
