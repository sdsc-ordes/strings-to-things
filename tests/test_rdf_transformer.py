import pytest
from rdflib import Graph, URIRef, Literal, Namespace
from strings2things.app.core.rdf_transformer import RDFTransformer

EX = Namespace("http://example.org/ontology#")


@pytest.fixture
def label_map():
    # Ontology label map: canonical labels → IRIs
    return {
        "geology": str(EX.Geology),
        "biology": str(EX.Biology),
        "physics": str(EX.Physics),
    }


@pytest.fixture
def input_graph():
    g = Graph()
    # Exact match example
    g.add((EX.subj1, EX.hasCategory, Literal("geology")))

    # Fuzzy match example (slightly misspelled)
    g.add((EX.subj2, EX.hasCategory, Literal("biolgy")))

    # Unknown label (should remain unchanged)
    g.add((EX.subj3, EX.hasCategory, Literal("unknownlabel")))

    # Non-literal value (should remain untouched)
    g.add((EX.subj4, EX.hasValue, URIRef("http://example.org/someIRI")))
    return g


def test_rdf_transformer_combined(label_map, input_graph):
    # Initialize transformer with fuzzy matching enabled
    transformer = RDFTransformer(label_map, fuzzy=True, fuzzy_threshold=80)
    output_graph = transformer.transform(input_graph)

    # --- 1. Check graph triples ---

    # Exact match: literal replaced by IRI
    assert (EX.subj1, EX.hasCategory, URIRef("http://example.org/ontology#Geology")) in output_graph

    # Fuzzy match: literal replaced by IRI
    assert (EX.subj2, EX.hasCategory, URIRef("http://example.org/ontology#Biology")) in output_graph

    # Unknown label: literal remains unchanged
    assert (EX.subj3, EX.hasCategory, Literal("unknownlabel")) in output_graph

    # Non-literals remain untouched
    assert (EX.subj4, EX.hasValue, URIRef("http://example.org/someIRI")) in output_graph

    # --- 2. Check log entries ---
    log = transformer.log.entries

    # Exact match log
    geology_log = next(e for e in log if e["original"] == "geology")
    assert geology_log["replacement"] == "http://example.org/ontology#Geology"
    assert geology_log["reason"] == "exact match"

    # Fuzzy match log
    biolgy_log = next(e for e in log if e["original"] == "biolgy")
    assert biolgy_log["replacement"] == "http://example.org/ontology#Biology"
    assert "fuzzy match" in biolgy_log["reason"]

    # Unknown label log
    unknown_log = next(e for e in log if e["original"] == "unknownlabel")
    assert unknown_log["replacement"] is None
    assert unknown_log["reason"] == "no match found"
