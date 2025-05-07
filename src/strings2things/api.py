import os
import tempfile

from fastapi import FastAPI, File, UploadFile
from typing import List

from .cli import strings_to_things, things_to_strings, initialize_graphs
from .queries import get_item_query

from SPARQLWrapper import SPARQLWrapper, JSON, QueryResult, TURTLE, CSV, JSONLD
import shutil

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

@app.post("/v1/loadOntology")
def load_ontology(files: List[UploadFile] = File(...)):
    """
    This api endpoint loads the ontology into the graphDB instance
    """

    ontology_dir = "/app/data/ontologies"
    os.makedirs(ontology_dir, exist_ok=True)

    for file in files:
        file_path = os.path.join(ontology_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return {"message": "Ontology loaded successfully"}

@app.get("/v1/strings2things")
def strings2things(item_uri: str, ontology_uri: str, kg_uri: str):
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

    #2b. Initiatlize the graph 
    dataset = initialize_graphs("/app/data/ontologies", temp_dir, ontology_uri, kg_uri)


    output_tmp_folder = tempfile.mkdtemp()
    output_file = os.path.join(output_tmp_folder, "output.ttl")
    #3. Provide the temporary folder to the string2things function
    # TODO: Obtain the output without intermediate files
    strings_to_things(dataset, output_file=os.path.join(temp_dir, output_file))

    #4 Read results from the output file
    with open(output_file, "rb") as f:
        output_data = f.read()

    print(output_data)

    #5. Upload the results to a graphDB instance

    #6. Provide the string-subgraph back to the user in jsonld

