# tests/conftest.py
import os
from pathlib import Path
from dotenv import load_dotenv
import pytest
from rdflib import Graph

# --- Environment Setup ---
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

from strings2things.app.config import Settings
from strings2things.app.core.ontology_manager import OntologyManager
from strings2things.app.core.rdf_transformer import RDFTransformer

settings = Settings()  # now environment variables are loaded
# --- Fixtures ---

@pytest.fixture
def ontology_manager():
    """
    Returns an OntologyManager with predicate-specific label maps built
    from examples/ontologies/test_ont.ttl
    """
    om = OntologyManager()
    om.graph.parse("examples/ontologies/test_ont.ttl", format="turtle")
    om._build_predicate_label_map()
    return om


@pytest.fixture
def input_graph():
    """
    Returns the input RDF graph from examples/data/test_data.ttl
    """
    g = Graph()
    g.parse("examples/data/test_data.ttl", format="turtle")
    return g


@pytest.fixture
def simple_label_map():
    """
    Returns a small label map for RDFTransformer unit tests
    """
    from rdflib import Namespace
    EX = Namespace("http://example.org/ontology#")
    return {
        "geology": str(EX.Geology),
        "biology": str(EX.Biology),
        "physics": str(EX.Physics),
    }
