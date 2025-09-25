from rdflib import Graph, Literal, URIRef, RDF, RDFS, XSD
from SPARQLWrapper import SPARQLWrapper, TURTLE
from strings2things.app.config import Settings

settings = Settings()


class OntologyManager:
    def __init__(self):
        self.graph = Graph()
        # Properly initialize as empty dict
        self.label_map: dict[str, dict[str, str]] = {}

    def load_ontologies(self):
        print(f"[INFO] Connecting to SPARQL endpoint: {settings.ONTOLOGY_SPARQL_ENDPOINT}")
        for graph_iri in settings.get_graph_iris():
            print(f"[INFO] Loading named graph: {graph_iri}")
            g = self._load_named_graph(settings.ONTOLOGY_SPARQL_ENDPOINT, graph_iri)
            self.graph += g
        print(f"[INFO] Loaded {len(self.graph)} triples.")
        self._build_predicate_label_map()

    def _load_named_graph(self, endpoint: str, graph_iri: str) -> Graph:
        sparql = SPARQLWrapper(endpoint)
        sparql.setCredentials(settings.GRAPHDB_USERNAME, settings.GRAPHDB_PASSWORD)
        sparql.setQuery(
            f"""
            CONSTRUCT {{ ?s ?p ?o }}
            WHERE {{
                GRAPH <{graph_iri}> {{ ?s ?p ?o }}
            }}
        """
        )
        sparql.setReturnFormat(TURTLE)
        result = sparql.query().convert()

        g = Graph()
        g.parse(data=result, format="turtle")
        return g
    
    def _check_predicate_ambiguities(
    self, predicate_map: dict[str, dict[str, str]]
) -> dict[str, dict[str, str]]:
        """
        Fail immediately if any predicate has duplicate labels.
        Returns the same map if no ambiguities are found.
        """
        for predicate, labels in predicate_map.items():
            seen: set[str] = set()
            duplicates: dict[str, list[str]] = {}

            for label, iri in labels.items():
                label_lower = label.lower().strip()
                if label_lower in seen:
                    duplicates.setdefault(label_lower, []).append(iri)
                else:
                    seen.add(label_lower)

            if duplicates:
                msg = (
                    f"Ambiguous labels detected for predicate {predicate}:\n"
                    + "\n".join(f"  '{lbl}' → {iris}" for lbl, iris in duplicates.items())
                )
                raise ValueError(msg)

        return predicate_map

    def _build_predicate_label_map(self):
        """
        Build a predicate-specific label map:
        {predicate_iri -> {label -> instance_iri}}
        Fail immediately if any predicate contains duplicate labels.
        """
        predicate_map: dict[str, dict[str, str]] = {}

        SH_CLASS = URIRef("http://www.w3.org/ns/shacl#class")
        SH_PATH = URIRef("http://www.w3.org/ns/shacl#path")
        SH_PROPERTY_SHAPE = URIRef("http://www.w3.org/ns/shacl#PropertyShape")

        for shape in self.graph.subjects(RDF.type, SH_PROPERTY_SHAPE):
            for predicate in self.graph.objects(shape, SH_PATH):
                predicate_iri = str(predicate)
                predicate_map[predicate_iri] = {}

                for cls in self.graph.objects(shape, SH_CLASS):
                    for instance in self.graph.subjects(RDF.type, cls):
                        for label_pred in [RDFS.label, URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")]:
                            for label in self.graph.objects(instance, label_pred):
                                if isinstance(label, Literal) and (not label.datatype or label.datatype == XSD.string):
                                    normalized_label = str(label).strip().lower()
                                    # Check if duplicate
                                    if normalized_label in predicate_map[predicate_iri]:
                                        raise ValueError(
                                            f"Ambiguous label '{normalized_label}' for predicate {predicate_iri}"
                                        )
                                    predicate_map[predicate_iri][normalized_label] = str(instance)

        self.label_map = predicate_map




    def get_predicate_label_map(self) -> dict[str, dict[str, str]]:
        """
        Returns the predicate-specific label map ready for RDFTransformer.
        """
        return self.label_map
