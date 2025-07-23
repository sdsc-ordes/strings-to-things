# app/utils/rdf_utils.py
"""
Helper functions for RDF parsing and serialization.
"""

from rdflib import Graph

def parse_rdf(content: bytes, format_hint: str = None) -> Graph:
    """
    Parse RDF content and return a Graph.
    """
    pass

def serialize_rdf(graph: Graph, output_format: str = "turtle") -> str:
    """
    Serialize a Graph to the specified RDF format.
    """
    pass
