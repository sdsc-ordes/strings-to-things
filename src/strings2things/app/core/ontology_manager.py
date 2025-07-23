from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, TURTLE
from strings2things.app import config
from rdflib import Literal
from rdflib import XSD

class OntologyManager:
    def __init__(self):
        self.graph = Graph()
        self.label_map: dict[str, str] = {}

    def load_ontologies(self):
        print(f"[INFO] Connecting to SPARQL endpoint: {config.ONTOLOGY_SPARQL_ENDPOINT}")
        for graph_iri in config.ONTOLOGY_GRAPH_IRIS:
            print(f"[INFO] Loading named graph: {graph_iri}")
            g = self._load_named_graph(config.ONTOLOGY_SPARQL_ENDPOINT, graph_iri)
            self.graph += g
        print(f"[INFO] Loaded {len(self.graph)} triples.")
        self._build_label_map()

    def _load_named_graph(self, endpoint: str, graph_iri: str) -> Graph:
        sparql = SPARQLWrapper(endpoint)
        sparql.setCredentials(config.GRAPHDB_USERNAME, config.GRAPHDB_PASSWORD)
        sparql.setQuery(f"""
            CONSTRUCT {{ ?s ?p ?o }}
            WHERE {{
                GRAPH <{graph_iri}> {{ ?s ?p ?o }}
            }}
        """)
        sparql.setReturnFormat(TURTLE)
        result = sparql.query().convert()

        g = Graph()
        g.parse(data=result, format="turtle")
        return g



    def _build_label_map(self):
        seen = {}
        for s, p, o in self.graph:
            if str(p) not in (
                "http://www.w3.org/2000/01/rdf-schema#label",
                "http://www.w3.org/2004/02/skos/core#prefLabel",
            ):
                continue

            # Only process literals (strings), skip others
            if not isinstance(o, Literal):
                continue

            # Only accept literals of type string or with language tags
            if o.datatype and o.datatype != XSD.string:
                # Skip non-string typed literals (e.g. numbers, dates)
                continue

            # Now get label text (lowercase, stripped)
            label = str(o).strip().lower()
            iri = str(s)

            if label in seen:
                if seen[label] != iri:
                    # Ambiguous label; remove from map
                    self.label_map.pop(label, None)
                    continue
            else:
                seen[label] = iri
                self.label_map[label] = iri

        print(f"[INFO] Label map built with {len(self.label_map)} unambiguous labels.")

    def get_label_map(self) -> dict[str, str]:
        return self.label_map
