from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, TURTLE
from strings2things.app.config import Settings
from rdflib import Literal
from rdflib import XSD

settings = Settings()

class OntologyManager:
    def __init__(self):
        self.graph = Graph()
        self.label_map: dict[str, str] = {}

    def load_ontologies(self):
        print(f"[INFO] Connecting to SPARQL endpoint: {settings.ONTOLOGY_SPARQL_ENDPOINT}")
        for graph_iri in settings.get_graph_iris():
            print(f"[INFO] Loading named graph: {graph_iri}")
            g = self._load_named_graph(settings.ONTOLOGY_SPARQL_ENDPOINT, graph_iri)
            self.graph += g
        print(f"[INFO] Loaded {len(self.graph)} triples.")
        self._build_label_map()

    def _load_named_graph(self, endpoint: str, graph_iri: str) -> Graph:
        sparql = SPARQLWrapper(endpoint)
        sparql.setCredentials(settings.GRAPHDB_USERNAME, settings.GRAPHDB_PASSWORD)
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

            if not isinstance(o, Literal):
                continue

            if o.datatype and o.datatype != XSD.string:
                continue

            label = str(o).strip().lower()
            iri = str(s)

            if label in seen:
                if seen[label] != iri:
                    # Mark ambiguity by storing list of IRIs
                    if isinstance(seen[label], list):
                        seen[label].append(iri)
                    else:
                        seen[label] = [seen[label], iri]
            else:
                seen[label] = iri

        # Check ambiguities and build final label_map
        self.label_map = self._check_ambiguities(seen)
        print(f"[INFO] Label map built with {len(self.label_map)} unambiguous labels.")

    def _check_ambiguities(self, seen: dict[str, str | list[str]]) -> dict[str, str]:
        ambiguous_labels = {label for label, iris in seen.items() if isinstance(iris, list)}

        if ambiguous_labels:
            msg = f"Found ambiguous labels: {', '.join(sorted(ambiguous_labels))} \n Please resolve these in your ontology before proceeding."
            if settings.FAIL_ON_AMBIGUOUS_LABELS:
                raise ValueError(msg)
            else:
                print(f"[WARNING] {msg}")

        # Return only unambiguous labels (those with a single IRI string)
        return {label: iris for label, iris in seen.items() if not isinstance(iris, list)}

    def get_label_map(self) -> dict[str, str]:
        return self.label_map
