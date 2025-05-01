from dotenv import load_dotenv
from strings2things.config import args

# Load environment variables from the .env file
load_dotenv()

# Parse graph names from command-line arguments
# Assign graph names
INSTANCE_DATA_GRAPH = args.kg_uri
ONTOLOGY_GRAPH = args.ontology_uri

strings_to_things_query = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX sh: <http://www.w3.org/ns/shacl#>

CONSTRUCT {{
    ?s ?p ?finalValue .
}}
WHERE {{
    GRAPH <{INSTANCE_DATA_GRAPH}> {{
        ?s ?p ?o .
    }}

    # Find the expected enumeration class for this property
    GRAPH <{ONTOLOGY_GRAPH}> {{
        OPTIONAL {{
            ?propertyShape sh:path ?p ;
                           sh:class ?expectedEnumClass .

            ?enumInstance rdf:type*/rdfs:subClassOf* ?expectedEnumClass ;
                          rdfs:label ?o .
        }}
    }}

    # Choose only one matching IRI per string, ensuring correct category
    BIND(COALESCE(?enumInstance, ?o) AS ?finalValue)
}}
"""

things_to_strings_query = f"""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX sh: <http://www.w3.org/ns/shacl#>

CONSTRUCT {{
    ?s ?p ?finalValue .
}}
WHERE {{
    GRAPH <{INSTANCE_DATA_GRAPH}> {{
        ?s ?p ?o .
    }}

    # Get the expected enum class for this property
    GRAPH <{ONTOLOGY_GRAPH}> {{
        OPTIONAL {{
            ?propertyShape sh:path ?p ;
                           sh:class ?expectedEnumClass .

            ?o a ?expectedEnumClass ;
               rdfs:label ?label .
        }}
    }}

    # If a label is found (meaning ?o is an enum instance), use it; otherwise keep the original value
    BIND(COALESCE(?label, ?o) AS ?finalValue)
}}
"""

def get_item_query(repo):
    """
    This function generates a SPARQL query to retrieve the subgraph of a given repository.
    It constructs a query that retrieves the subject, predicate, and object of the repository,
    along with additional properties and values.

    Args:
        repo (str): The URI of the repository.

    Returns:
        str: The SPARQL query string.
    """
    item_query = f"""
        PREFIX : <https://imaging-plaza.epfl.ch/>
        CONSTRUCT {{
        ?subject ?predicate ?object .
        ?object ?p ?o .
        ?o ?something ?else .
        }} WHERE {{
        GRAPH <${INSTANCE_DATA_GRAPH}{{
            {{
            {{?subject ?predicate ?object .
            filter(?subject = <${repo}> )
            OPTIONAL {{ ?object ?p ?o . 
            OPTIONAL {{?o ?something ?else}}
                    }}}}}}}}}} 
    """

    return item_query