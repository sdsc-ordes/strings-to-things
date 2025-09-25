# app/core/rdf_transformer.py
"""
Transforms RDF graphs by replacing string literals with matching ontology IRIs.
Supports exact and fuzzy matching (RapidFuzz).
"""

from rdflib import Graph, Literal, URIRef
from strings2things.app.core.transformation_log import TransformationLog
from rapidfuzz import process


class RDFTransformer:
    def __init__(self, predicate_label_map: dict[str, dict[str, str]], fuzzy: bool, fuzzy_threshold: int = 90):
        """
        :param predicate_label_map: {predicate_iri: {label -> IRI}}
        """
        self.predicate_label_map = predicate_label_map
        self.fuzzy = fuzzy
        self.fuzzy_threshold = fuzzy_threshold
        self.log = TransformationLog()

    def _find_match(self, predicate: str, label: str) -> str | None:
        label = label.strip().lower()
        label_map = self.predicate_label_map.get(predicate, {})

        # Exact match
        iri = label_map.get(label)
        if iri:
            return iri

        # Fuzzy fallback
        if self.fuzzy and label_map:
            best = process.extractOne(label, label_map.keys())
            if best:
                match, score, _ = best
                if score >= self.fuzzy_threshold:
                    return label_map[match]

        return None

    def transform(self, input_graph: Graph) -> Graph:
        output_graph = Graph()

        for s, p, o in input_graph:
            iri_str = None
            if isinstance(o, Literal) and isinstance(o.value, str):
                iri_str = self._find_match(str(p), o.value)
                if iri_str:
                    iri = URIRef(iri_str)
                    output_graph.add((s, p, o))
                    output_graph.add((iri, URIRef("http://www.example.org/thingOf"), o))
                    output_graph.add((s, p, iri))
                    self.log.add_entry(
                        subject=str(s),
                        predicate=str(p),
                        original_value=str(o),
                        replacement_iri=str(iri),
                        reason="exact match" if o.value.strip().lower() in self.predicate_label_map.get(str(p), {}) else f"fuzzy match (threshold={self.fuzzy_threshold})",
                    )
                    continue

            output_graph.add((s, p, o))
            self.log.add_entry(
                subject=str(s),
                predicate=str(p),
                original_value=str(o),
                replacement_iri=None,
                reason="not a string literal" if not isinstance(o, Literal) else "no match found",
            )

        return output_graph
