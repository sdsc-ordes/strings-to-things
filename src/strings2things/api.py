import os
import tempfile

from fastapi import FastAPI

from cli import strings_to_things, things_to_strings
from queries import get_item_query

from SPARQLWrapper import SPARQLWrapper, JSON, QueryResult, TURTLE, CSV, JSONLD

app = FastAPI()

@app.get("/")
def index():
    return {"title": "strings2things", "description": "", "version": "0.1"}

def get_data_from_graphdb(db_host: str, 
                          db_user: str, 
                          db_password: str,
                          item_uri: str,
                          graph:str) -> bytes:
    """
    Get data from GraphDB.

    Args:
        db_host: The host URL of the GraphDB.
        db_user: The username for authentication.
        db_password: The password for authentication.
        softwareURI: Indentifier of target software
        graph: Graph where the entry is located

    Returns:
        The data as a bytes object.
    """

    item_query = get_item_query(item_uri, graph)

    sparql = SPARQLWrapper(db_host)
    sparql.setQuery(item_query)
    sparql.setReturnFormat(TURTLE)
    sparql.setCredentials(user=db_user, passwd=db_password)
    results = sparql.query().convert()
    return results

@app.get("/v1/string2things")
def string2things(item_uri: str):
    """
    This api endpoint takes an URI and is able to retrieve the subgraph from a graphDB instance
    Then it will run string2things on the subgraph and upload the results to a graphDB instance
    In parallel it will provide an string-subgraph back to the user in jsonld

    (BONUS) In a future this tool will enrich the output looking for things with LLM
    """

    #1. Get the subgraph from the graphDB instance
    response = get_data_from_graphdb(db_host=os.environ["GRAPHDB_URL"],
                                     db_user=os.environ["GRAPHDB_USER"],
                                     db_password=os.environ["GRAPHDB_PASSWORD"],
                                     item_uri=item_uri,
                                     graph=os.environ["KNOWLEDGE_GRAPH_URI"])

    #2. Store the result in a temporary file / folder
    temp_dir = tempfile.mkdtemp()
    ttl_file_path = os.path.join(temp_dir, "subgraph.ttl")
    with open(ttl_file_path, "wb") as f:
        f.write(response)

    #3. Provide the temporary folder to the string2things function
    strings_to_things()

    #4. Run the string2things function

    #5. Upload the results to a graphDB instance

    #6. Provide the string-subgraph back to the user in jsonld