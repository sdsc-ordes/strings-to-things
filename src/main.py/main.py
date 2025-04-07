import dotenv
import os

dotenv.load_dotenv()

apikey = os.getenv("OPEN-AI-KEY")

print(apikey)

from agents import Agent, ModelSettings, function_tool
import rdflib
knowledge_graph_path = os.getenv("KNOWLEDGE_GRAPH_PATH")

ontologies_path = os.getenv("ONTOLOGIES_PATH")

# Load the knowledge graph

# SPARQLwrapper
onto = rdflib.Graph()
onto.parse(knowledge_graph_path)

#Query
query = r"""
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?o

WHERE {
    ?s ?p ?o .
    FILTER (!(?p IN (schema:name, schema:description, rdfs:comment, skos:definition)))
    FILTER (!regex(STR(?o), "^[ \t]*https?://"))
	FILTER (!regex(STR(?o), "^\\d{4}-\\d{2}-\\d{2}T00:00:00\\.000Z$"))
    FILTER (datatype(?o) = xsd:string)
    }
"""
results = onto.query(query)
# Print the results
for row in results:
    print(row.o)
#count the number of rows:
print("Number of rows: ", len(results))
# Find all objects of triples that are strings (Agent 1 using SPARQL SELECT query)

# Attempt to match those strings to strings in the ontology (Agent 2 - FUZON )
# 
# If it does not find a match - (Agent 3 - LLM agent)

# Validate whether the returned match actually exists in one of the ontologies (Agent 4 - SPARQL (ask query))

# If it finds an IRI with the string as it's object, it will replace the string in the knowledge graph with the IRI

# Return the new and improved knowledge graph

agent = "4o-mini"


