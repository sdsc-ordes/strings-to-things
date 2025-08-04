# app/core/rdf_transformer.py
"""
Transforms RDF graphs by replacing string literals with matching ontology IRIs.
"""

from rdflib import Graph, Literal, URIRef
from strings2things.app.core.transformation_log import TransformationLog


class RDFTransformer:
    def __init__(self, label_map: dict[str, str]):
        self.label_map = label_map
        self.log = TransformationLog()

    def transform(self, input_graph: Graph) -> Graph:
        """
        Replace matching string literals in the RDF graph with IRIs.
        Returns a transformed RDFLib Graph.
        """
        output_graph = Graph()

        for s, p, o in input_graph:
            # if string matches object
            if isinstance(o, Literal) and isinstance(o.value, str):
                label = o.value.strip().lower()
                if label in self.label_map:
                    iri = URIRef(self.label_map[label])

                    # Retain original triple (to retain backward compatibility for now)
                    output_graph.add((s, p, o))
                    output_graph.add(
                        (iri, URIRef("http://wwww.example.org/thingOf"), o)
                    )

                    output_graph.add((s, p, iri))

                    self.log.add_entry(
                        subject=str(s),
                        predicate=str(p),
                        original_value=str(o),
                        replacement_iri=str(iri),
                        reason="unambiguous match",
                    )
                    continue

            output_graph.add((s, p, o))
            self.log.add_entry(
                subject=str(s),
                predicate=str(p),
                original_value=str(o),
                replacement_iri=None,
                reason=(
                    "not a string literal"
                    if not isinstance(o, Literal)
                    else "no match in label map"
                ),
            )

        return output_graph
