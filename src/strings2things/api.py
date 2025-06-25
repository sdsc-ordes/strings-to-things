import os
import tempfile
import shutil
import uuid

from fastapi import FastAPI, File, UploadFile, Response
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, POSTDIRECTLY
import requests
from dotenv import load_dotenv

from .cli import strings_to_things, initialize_graphs, things_to_strings
load_dotenv()

app = FastAPI()

GRAPHDB_URL = os.environ["GRAPHDB_URL"]
GRAPHDB_USER = os.environ["GRAPHDB_USER"]
GRAPHDB_PASSWORD = os.environ["GRAPHDB_PASSWORD"]
ONTOLOGY_URI = os.environ["ONTOLOGY_URI"]
ONTOLOGY_DIR = os.environ["ONTOLOGIES_PATH"]


@app.on_event("startup")
def load_ontologies():
    for fname in os.listdir(ONTOLOGY_DIR):
        path = os.path.join(ONTOLOGY_DIR, fname)
        g = Graph()
        g.parse(path, format="turtle")
        data = g.serialize(format="turtle")
        response = requests.post(
            url=f"{GRAPHDB_URL}?context=<{ONTOLOGY_URI}>",
            headers={"Content-Type": "text/turtle"},
            auth=(GRAPHDB_USER, GRAPHDB_PASSWORD),
            data=data.encode("utf-8"),
        )
        response.raise_for_status()


@app.post("/v1/strings2things")
def strings2things_endpoint(file: UploadFile = File(...)):
    kg_uri = f"http://temp.org/kg/{uuid.uuid4()}"

    with tempfile.TemporaryDirectory() as tmpdir:
        kg_path = os.path.join(tmpdir, file.filename)
        with open(kg_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        g = Graph()
        g.parse(kg_path, format="turtle")
        data = g.serialize(format="turtle")

        response = requests.post(
            url=f"{GRAPHDB_URL}?context=<{kg_uri}>",
            headers={"Content-Type": "text/turtle"},
            auth=(GRAPHDB_USER, GRAPHDB_PASSWORD),
            data=data,
        )
        response.raise_for_status()

        dataset = initialize_graphs(ONTOLOGY_DIR, tmpdir, ONTOLOGY_URI, kg_uri)
        output_file = os.path.join(tmpdir, "output.ttl")
        strings_to_things(dataset, output_file, kg_uri, ONTOLOGY_URI)

        with open(output_file, "rb") as f:
            output_data = f.read()

        delete_query = f"CLEAR GRAPH <{kg_uri}>"

        sparql = SPARQLWrapper(f"{GRAPHDB_URL}")
        sparql.setCredentials(GRAPHDB_USER, GRAPHDB_PASSWORD)
        sparql.setMethod(POSTDIRECTLY)
        sparql.setRequestMethod(POSTDIRECTLY)
        sparql.setQuery(delete_query)
        sparql.query()

    return Response(content=output_data, media_type="text/turtle")

@app.post("/v1/things2strings")
def things2strings_endpoint(file: UploadFile = File(...)):
    kg_uri = f"http://temp.org/kg/{uuid.uuid4()}"

    with tempfile.TemporaryDirectory() as tmpdir:
        kg_path = os.path.join(tmpdir, file.filename)
        with open(kg_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        g = Graph()
        g.parse(kg_path, format="turtle")
        data = g.serialize(format="turtle")

        response = requests.post(
            url=f"{GRAPHDB_URL}?context=<{kg_uri}>",
            headers={"Content-Type": "text/turtle"},
            auth=(GRAPHDB_USER, GRAPHDB_PASSWORD),
            data=data,
        )
        response.raise_for_status()

        dataset = initialize_graphs(ONTOLOGY_DIR, tmpdir, ONTOLOGY_URI, kg_uri)
        output_file = os.path.join(tmpdir, "output.ttl")
        things_to_strings(dataset, output_file, kg_uri, ONTOLOGY_URI)

        with open(output_file, "rb") as f:
            output_data = f.read()

        delete_query = f"CLEAR GRAPH <{kg_uri}>"

        sparql = SPARQLWrapper(f"{GRAPHDB_URL}")
        sparql.setCredentials(GRAPHDB_USER, GRAPHDB_PASSWORD)
        sparql.setMethod(POSTDIRECTLY)
        sparql.setRequestMethod(POSTDIRECTLY)
        sparql.setQuery(delete_query)
        sparql.query()

    return Response(content=output_data, media_type="text/turtle")
