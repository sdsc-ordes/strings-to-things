enumeration_query = r"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

construct { ?subject ?predicate ?object }
WHERE {
    ?subject a schema:Enumeration .
    ?subject ?predicate ?object .
}
"""

find_matches_query = r"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

CONSTRUCT {
    ?s ?p ?result .
}
WHERE {
    GRAPH <https://imaging-plaza.epfl.ch/finalGraph> {
        ?s ?p ?o .
        FILTER (!(?p IN (schema:name, schema:description, rdfs:comment, skos:definition)))
        FILTER (!regex(STR(?o), "^[ \t]*https?://"))
        FILTER (!regex(STR(?o), "^\\d{4}-\\d{2}-\\d{2}T00:00:00\\.000Z$"))
        FILTER (datatype(?o) = xsd:string)
    }
    GRAPH <https://imaging-plaza.epfl.ch/ontology#enums> {
        OPTIONAL {
            ?s2 rdfs:label ?o.
        }

        # Ensure only one IRI is bound to the label, skipping rows with multiple IRIs
        FILTER NOT EXISTS {
            ?s3 rdfs:label ?o.
            FILTER (?s3 != ?s2)  # Ensures ?s2 is the only IRI bound to the label
        }
    }

    BIND(IF(BOUND(?s2), ?s2, ?o) AS ?result)
}
"""

find_predicate_query = r"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?o ?p
WHERE {
    ?s ?p ?o .
        FILTER (!(?p IN (schema:name, schema:description, rdfs:comment, skos:definition)))
        FILTER (!regex(STR(?o), "^[ \t]*https?://"))
        FILTER (!regex(STR(?o), "^\\d{4}-\\d{2}-\\d{2}T00:00:00\\.000Z$"))
        FILTER (datatype(?o) = xsd:string)
}"""
