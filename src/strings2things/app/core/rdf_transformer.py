# app/core/rdf_transformer.py
"""
Transforms RDF graphs by replacing string literals with matching ontology IRIs.
Supports exact and fuzzy matching (RapidFuzz).
"""

from rdflib import Graph, Literal, URIRef
from strings2things.app.core.transformation_log import TransformationLog
from rapidfuzz import process


class RDFTransformer:
    def __init__(self, label_map: dict[str, str], fuzzy: bool, fuzzy_threshold: int = 90):
        """
        :param label_map: dict of {label -> IRI}
        :param fuzzy_threshold: minimum score for fuzzy fallback
        """
        self.label_map = label_map
        self.fuzzy = fuzzy
        self.fuzzy_threshold = fuzzy_threshold
        self.log = TransformationLog()

    def _find_match(self, label: str) -> str | None:
        """
        Find an IRI for the given label.
        First tries exact match, then falls back to fuzzy.
        """
        label = label.strip().lower()

        # Exact match
        if label in self.label_map:
            return self.label_map[label]

        # Fuzzy fallback
        best = process.extractOne(label, self.label_map.keys())
        if best:
            match, score, _ = best
            if score >= self.fuzzy_threshold:
                return self.label_map[match]

        return None

    def transform(self, input_graph: Graph) -> Graph:
        """
        Replace matching string literals in the RDF graph with IRIs.
        Returns a transformed RDFLib Graph.
        """
        output_graph = Graph()

        for s, p, o in input_graph:
            if isinstance(o, Literal) and isinstance(o.value, str):
                iri_str = self._find_match(o.value)
                if iri_str:
                    iri = URIRef(iri_str)

                    # Retain original triple (for backward compatibility)
                    output_graph.add((s, p, o))
                    output_graph.add((iri, URIRef("http://www.example.org/thingOf"), o))
                    output_graph.add((s, p, iri))

                    self.log.add_entry(
                        subject=str(s),
                        predicate=str(p),
                        original_value=str(o),
                        replacement_iri=str(iri),
                        reason="exact match"
                        if o.value.strip().lower() in self.label_map
                        else f"fuzzy match (threshold={self.fuzzy_threshold})",
                    )
                    continue

            # If no match found → leave as-is
            output_graph.add((s, p, o))
            self.log.add_entry(
                subject=str(s),
                predicate=str(p),
                original_value=str(o),
                replacement_iri=None,
                reason=(
                    "not a string literal"
                    if not isinstance(o, Literal)
                    else "no match found"
                ),
            )

        return output_graph
