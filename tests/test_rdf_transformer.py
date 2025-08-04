import pytest
from rdflib import Graph, URIRef, Literal, Namespace
from strings2things.app.core.rdf_transformer import RDFTransformer
from strings2things.app.core.transformation_log import TransformationLog

EX = Namespace("http://example.org/")


@pytest.fixture
def label_map():
    return {
        "geology": "http://example.org/ontology#Geology",
        "biology": "http://example.org/ontology#Biology",
    }


@pytest.fixture
def input_graph():
    g = Graph()
    g.add((EX.subj1, EX.hasCategory, Literal("Geology")))
    g.add((EX.subj2, EX.hasCategory, Literal("UnknownLabel")))
    g.add((EX.subj3, EX.hasValue, URIRef("http://example.org/someIRI")))
    return g


def test_rdf_transformer(label_map, input_graph):
    transformer = RDFTransformer(label_map)
    output_graph = transformer.transform(input_graph)

    # --- Check graph triples ---
    # Original triple must remain
    assert (EX.subj1, EX.hasCategory, Literal("Geology")) in output_graph

    # Transformed triple must be present
    expected_iri = URIRef("http://example.org/ontology#Geology")
    assert (EX.subj1, EX.hasCategory, expected_iri) in output_graph

    # UnknownLabel should remain unchanged (no IRI added)
    assert (EX.subj2, EX.hasCategory, Literal("UnknownLabel")) in output_graph
    assert len([t for t in output_graph.triples((EX.subj2, EX.hasCategory, None))]) == 1

    # Non-literals should remain untouched
    assert (EX.subj3, EX.hasValue, URIRef("http://example.org/someIRI")) in output_graph

    # --- Check log entries ---
    log = transformer.log.entries
    geology_log = next(e for e in log if e["original"] == "Geology")
    assert geology_log["replacement"] == "http://example.org/ontology#Geology"
    assert geology_log["reason"] == "unambiguous match"

    unknown_log = next(e for e in log if e["original"] == "UnknownLabel")
    assert unknown_log["replacement"] is None
    assert unknown_log["reason"] == "no match in label map"
