# app/api/endpoints.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response
from rdflib import Graph
from src.strings2things.app.core.rdf_transformer import RDFTransformer
from src.strings2things.app.core.ontology_manager import OntologyManager # Assume this exists
from src.strings2things.app.utils.rdf_utils import parse_rdf, serialize_rdf  # Also assume or create
import logging

router = APIRouter()

# ✅ Initialize and load ontologies at startup
ontology_manager = OntologyManager()
ontology_manager.load_ontologies()

# ✅ Build RDFTransformer with the label map
transformer = RDFTransformer(ontology_manager.get_label_map())

@router.post("/transform")
async def transform_rdf(
    file: UploadFile = File(...),
    serialization: str = Form("turtle")
) -> Response:
    """
    Accepts an RDF file upload, transforms it using the label map,
    and returns the modified RDF graph in the requested format.
    """
    content = await file.read()

    try:
        input_graph = parse_rdf(content)
        transformed_graph = transformer.transform(input_graph)
        serialized = serialize_rdf(transformed_graph, output_format=serialization)

        return Response(content=serialized, media_type="text/plain")

    except Exception as e:
        logging.exception("Transformation failed")
        return Response(content=str(e), status_code=400)
