import dotenv
import os

dotenv.load_dotenv()

apikey = os.getenv("OPEN-AI-KEY")

from agents import Agent, ModelSettings, function_tool
import rdflib
from pyfuzon.matcher import TermMatcher


knowledge_graph_path = os.getenv("KNOWLEDGE_GRAPH_PATH")

ontologies_path = os.getenv("ONTOLOGIES_PATH")
# SPARQLwrapper
dataset = rdflib.Dataset()

onto = dataset.graph("https://imaging-plaza.epfl.ch/ontology#")
onto.parse(ontologies_path)

data = dataset.graph("https://imaging-plaza.epfl.ch/finalGraph")
data.parse(knowledge_graph_path)
# Load the knowledge graph


#Query
query = r"""
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
    GRAPH <https://imaging-plaza.epfl.ch/ontology#> {
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
results = dataset.query(query)
# Print the results
for row in results:
    print(row)

# Create a new graph to store the constructed triples
constructed_graph = rdflib.Graph()

# Add the results of the CONSTRUCT query to the new graph
for triple in results.graph:
    constructed_graph.add(triple)


matcher = TermMatcher.from_files([ontologies_path])
matcher.terms #accesses the list of terms loaded from input files
searchterm = "query"
if sorted(matcher.score(searchterm), reverse= True )[0] > 0.5:
    print(matcher.top(searchterm, 1)) # shows the top match


else:
    print("########### GET WRECKED NOOB 😎💥🔥👑 ###########")
# Attempt to match those strings to strings in the ontology (Agent 2 - FUZON )
# 
# If it does not find a match - (Agent 3 - LLM agent)

# Validate whether the returned match actually exists in one of the ontologies (Agent 4 - SPARQL (ask query))

# If it finds an IRI with the string as it's object, it will replace the string in the knowledge graph with the IRI

# Return the new and improved knowledge graph

agent = "4o-mini"


