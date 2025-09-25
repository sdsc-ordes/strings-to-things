# app/api/endpoints.py

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response
from rdflib import Graph
from strings2things.app.core.rdf_transformer import RDFTransformer
from strings2things.app.core.ontology_manager import OntologyManager
from strings2things.app.utils.rdf_utils import parse_rdf, serialize_rdf
import logging

router = APIRouter()

ontology_manager = OntologyManager()
ontology_manager.load_ontologies()

# Keep transformer as a base instance
base_label_map = ontology_manager.get_predicate_label_map()


@router.post("/transform")
async def transform_rdf(
    file: UploadFile = File(...),
    serialization: str = Form("turtle"),
    fuzzy: bool = Form(False),  # <-- new parameter
    fuzzy_threshold: int = Form(90),  # <-- configurable fuzzy matching threshold
) -> Response:
    """
    Accepts an RDF file upload, transforms it using the label map,
    and returns the modified RDF graph in the requested format.

    Args:
        file: The uploaded RDF file
        serialization: Desired output RDF serialization (default: turtle)
        fuzzy: Whether to use fuzzy matching (default: False)
        threshold: Similarity threshold for fuzzy matching (0-100, default: 90)
    """
    content = await file.read()

    try:
        input_graph = parse_rdf(content)

        transformer = RDFTransformer(
            base_label_map,
            fuzzy=fuzzy,
            fuzzy_threshold=fuzzy_threshold,
        )

        transformed_graph = transformer.transform(input_graph)
        serialized = serialize_rdf(transformed_graph, output_format=serialization)

        return Response(content=serialized, media_type="text/plain")

    except Exception as e:
        logging.exception("Transformation failed")
        return Response(content=str(e), status_code=400)
