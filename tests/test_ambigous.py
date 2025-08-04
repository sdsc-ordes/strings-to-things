import pytest
from rdflib import Graph, URIRef, Literal
from strings2things.app.core.ontology_manager import OntologyManager
import strings2things.app.config as config_module

settings = config_module.Settings()  # use the global settings instance your app uses


def create_ambiguous_graph():
    g = Graph()
    g.add(
        (
            URIRef("http://example.org/resource1"),
            URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
            Literal("ambiguouslabel"),
        )
    )
    g.add(
        (
            URIRef("http://example.org/resource2"),
            URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
            Literal("ambiguouslabel"),
        )
    )
    return g


def test_ambiguous_labels_detection_fail(monkeypatch):
    monkeypatch.setattr(
        "strings2things.app.core.ontology_manager.settings.FAIL_ON_AMBIGUOUS_LABELS",
        True,
    )

    manager = OntologyManager()
    manager.graph = create_ambiguous_graph()

    with pytest.raises(ValueError) as exc_info:
        manager._build_label_map()
    assert "ambiguouslabel" in str(exc_info.value)


def test_ambiguous_labels_detection_no_fail(monkeypatch):
    # Patch the *module-level* settings inside ontology_manager to False
    monkeypatch.setattr(
        "strings2things.app.core.ontology_manager.settings.FAIL_ON_AMBIGUOUS_LABELS",
        False,
    )

    manager = OntologyManager()
    manager.graph = create_ambiguous_graph()

    # Should NOT raise ValueError
    try:
        manager._build_label_map()
    except ValueError:
        pytest.fail("ValueError raised even though FAIL_ON_AMBIGUOUS_LABELS is False")

    # The ambiguous label should not be in the map
    assert "ambiguouslabel" not in manager.get_label_map()
