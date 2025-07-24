# app/config.py
"""
Configuration for ontology loading and runtime behavior.
"""

import os
from dotenv import load_dotenv

load_dotenv()
GRAPHDB_USERNAME = os.getenv("GRAPHDB_USERNAME")
GRAPHDB_PASSWORD = os.getenv("GRAPHDB_PASSWORD")

ONTOLOGY_SPARQL_ENDPOINT = os.getenv("ONTOLOGY_SPARQL_ENDPOINT")
ONTOLOGY_GRAPH_IRIS = [
    iri.strip() for iri in os.getenv("ONTOLOGY_GRAPH_IRIS", "").split(",") if iri.strip()
]

if not ONTOLOGY_SPARQL_ENDPOINT or not ONTOLOGY_GRAPH_IRIS:
    raise ValueError("Must provide ONTOLOGY_SPARQL_ENDPOINT and ONTOLOGY_GRAPH_IRIS in .env")
