import os
import tempfile

from fastapi import FastAPI

from cli import strings_to_things, things_to_strings

import json

app = FastAPI()

@app.get("/")
def index():
    return {"title": "strings2things", "description": "", "version": "0.1"}

@app.get("/v1/string2things")
def string2things():
    """
    This api endpoint takes an URI and is able to retrieve the subgraph from a graphDB instance
    Then it will run string2things on the subgraph and upload the results to a graphDB instance
    In parallel it will provide an string-subgraph back to the user in jsonld

    (BONUS) In a future this tool will enrich the output looking for things with LLM
    """

    #1. Get the subgraph from the graphDB instance

    #2. Store the result in a temporary file / folder

    #3. Provide the temporary folder to the string2things function

    #4. Run the string2things function

    #5. Upload the results to a graphDB instance

    #6. Provide the string-subgraph back to the user in jsonld

    pass