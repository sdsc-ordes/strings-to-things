# app/utils/rdf_utils.py
"""
Helper functions for RDF parsing and serialization.
"""

from rdflib import Graph
from rdflib.plugin import PluginException


def parse_rdf(data: bytes, format: str | None = None) -> Graph:
    """
    Parses RDF data from bytes. Tries to guess format if not provided.

    Args:
        data: RDF content as bytes.
        format: Optional RDF format (e.g., 'turtle', 'xml', 'json-ld').

    Returns:
        A parsed RDFLib Graph.

    Raises:
        ValueError: If the data cannot be parsed.
    """
    g = Graph()

    try:
        # First try with explicit format (if given)
        g.parse(data=data, format=format)
        return g

    except PluginException as e:
        raise ValueError(f"Unsupported RDF format: {format}") from e

    except Exception as e:
        raise ValueError("Failed to parse RDF input.") from e


from rdflib import Graph


def serialize_rdf(graph: Graph, output_format: str = "turtle") -> str:
    """
    Serialize an RDFLib Graph to the specified RDF format.

    Args:
        graph (Graph): The RDFLib graph to serialize.
        output_format (str): The desired RDF serialization format (e.g., "turtle", "xml", "nt", "json-ld").

    Returns:
        str: The serialized RDF data as a string.
    """
    return (
        graph.serialize(format=output_format).decode("utf-8")
        if isinstance(graph.serialize(format=output_format), bytes)
        else graph.serialize(format=output_format)
    )
