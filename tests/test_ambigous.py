# tests/test_ambiguous.py
import pytest
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from strings2things.app.core.ontology_manager import OntologyManager

SH = "http://www.w3.org/ns/shacl#"
EX = "http://example.org/"

def create_mock_ontology_graph_with_duplicates() -> Graph:
    """
    Returns a mock ontology graph containing:
    - A PropertyShape constrained to a class
    - Two instances of that class with the same label
    """
    g = Graph()

    # Define a PropertyShape
    prop_shape = URIRef(EX + "hasCategoryShape")
    g.add((prop_shape, RDF.type, URIRef(SH + "PropertyShape")))
    g.add((prop_shape, URIRef(SH + "path"), URIRef(EX + "hasCategory")))
    g.add((prop_shape, URIRef(SH + "class"), URIRef(EX + "Category")))

    # Two instances of Category with the same label
    instance1 = URIRef(EX + "cat1")
    instance2 = URIRef(EX + "cat2")
    g.add((instance1, RDF.type, URIRef(EX + "Category")))
    g.add((instance2, RDF.type, URIRef(EX + "Category")))
    g.add((instance1, RDFS.label, Literal("ambiguouslabel")))
    g.add((instance2, RDFS.label, Literal("ambiguouslabel")))

    return g


@pytest.fixture
def ontology_manager_with_duplicates() -> OntologyManager:
    """
    Return an OntologyManager instance with the mocked duplicate-ontology graph.
    """
    manager = OntologyManager()
    manager.graph = create_mock_ontology_graph_with_duplicates()
    return manager


def test_ambiguous_labels_detection_raises(ontology_manager_with_duplicates):
    """
    Ensure that _build_predicate_label_map raises ValueError if there are duplicate labels
    within the same predicate/class.
    """
    manager = ontology_manager_with_duplicates
    with pytest.raises(ValueError) as exc_info:
        manager._build_predicate_label_map()

    # Check that the error message contains the duplicate label
    assert "ambiguouslabel" in str(exc_info.value)
