"""RDF transformation API endpoints.

We intentionally split raw-body and multipart upload into two endpoints so that
the generated OpenAPI schema (Swagger UI) shows both usage patterns. A single
endpoint mixing `UploadFile` with a normal JSON/Turtle body would appear only
as `multipart/form-data` in the docs.

Endpoints
---------
POST /v1/things         Raw JSON-LD (object/array) or Turtle string body
POST /v1/things/upload  Multipart file upload

Shared Parameters
-----------------
serialization  (required) jsonld | turtle
fuzzy          (optional, default false)
fuzzy_threshold (0-100, default 90)
"""

from __future__ import annotations

from typing import Literal
import json
import logging
from fastapi import APIRouter, UploadFile, File, Query, Form, Request, Body
from fastapi.responses import Response

from strings2things.app.core.rdf_transformer import RDFTransformer
from strings2things.app.core.ontology_manager import OntologyManager
from strings2things.app.utils.rdf_utils import parse_rdf, serialize_rdf

router = APIRouter()
ontology_manager = OntologyManager()  # Lazy load on first access


def _detect_input_format(content_type: str, data: bytes) -> str:
    """Infer whether payload is JSON-LD or Turtle.

    Uses explicit content-type when present; falls back to leading character
    heuristic (object/array starts imply JSON-LD).
    """
    ct = (content_type or "").split(";")[0].strip().lower()
    if ct in {"application/ld+json", "application/json"}:
        return "json-ld"
    if ct in {"text/turtle", "application/x-turtle", "text/plain"}:
        return "turtle"
    lead = data.lstrip()[:1]
    return "json-ld" if lead in (b"{", b"[") else "turtle"


def _label_map() -> dict[str, str]:
    if not ontology_manager.get_label_map():
        try:
            ontology_manager.load_ontologies()
        except Exception:  # pragma: no cover (resilience path)
            logging.exception("Ontology loading failed; proceeding with empty label map")
    return ontology_manager.get_label_map() or {}


def _transform_bytes(
    payload: bytes,
    content_type: str,
    serialization: Literal["jsonld", "turtle"],
    fuzzy: bool,
    fuzzy_threshold: int,
) -> tuple[str, str]:
    input_format = _detect_input_format(content_type, payload)
    graph = parse_rdf(payload, format=input_format)
    transformer = RDFTransformer(_label_map(), fuzzy=fuzzy, fuzzy_threshold=fuzzy_threshold)
    transformed = transformer.transform(graph)
    out_fmt = "json-ld" if serialization == "jsonld" else "turtle"
    media_type = "application/ld+json" if out_fmt == "json-ld" else "text/turtle"
    serialized = serialize_rdf(transformed, output_format=out_fmt)
    return serialized, media_type


@router.post(
    "/v1/things",
    tags=["transform"],
    summary="Transform RDF (raw body)",
    description=(
        "Send RDF as either JSON-LD (application/ld+json or application/json) or plain Turtle (text/turtle or text/plain). "
        "When sending Turtle, set the Content-Type header to text/turtle (no JSON wrapper needed)."
    ),
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/ld+json": {
                    "schema": {"type": "object", "description": "JSON-LD object graph"},
                    "examples": {
                        "jsonldObject": {
                            "summary": "Minimal JSON-LD",
                            "value": {"@context": {}, "@id": "_:b0", "name": "Example"},
                        }
                    },
                },
                "application/json": {
                    "schema": {"type": "object", "description": "Interpreted as JSON-LD"},
                    "examples": {
                        "genericJson": {
                            "summary": "Generic JSON treated as JSON-LD",
                            "value": {"label": "Some Value"},
                        }
                    },
                },
                "text/turtle": {
                    "schema": {"type": "string", "description": "Turtle serialization"},
                    "examples": {
                        "turtle": {
                            "summary": "Turtle example",
                            "value": "@prefix ex: <http://example/> . ex:s ex:p ex:o .",
                        }
                    },
                },
                "text/plain": {
                    "schema": {"type": "string", "description": "Plain text (assumed Turtle)"}
                },
            },
        }
    },
)
async def transform_rdf_raw(
    request: Request,
    serialization: Literal["jsonld", "turtle"] = Query(..., description="Output format"),
    fuzzy: bool = Query(False, description="Enable fuzzy matching"),
    fuzzy_threshold: int = Query(90, ge=0, le=100, description="Fuzzy threshold 0-100"),
) -> Response:
    """Accept raw body as JSON-LD or Turtle without requiring JSON wrapping for Turtle.

    We read the raw bytes to allow multiple media types. Format detection uses
    the Content-Type header first, then a leading character heuristic.
    """
    try:
        body = await request.body()
        if not body:
            return Response(content="Empty body", status_code=400)
        content_type = request.headers.get("content-type", "")
        serialized, media_type = _transform_bytes(
            body, content_type, serialization, fuzzy, fuzzy_threshold
        )
        return Response(content=serialized, media_type=media_type)
    except Exception as e:  # pragma: no cover
        logging.exception("Transformation failed")
        return Response(content=str(e), status_code=400)


@router.post(
    "/v1/things/upload",
    tags=["transform"],
    summary="Transform RDF (file upload)",
    description="Upload an RDF file (JSON-LD or Turtle) via multipart/form-data",
)
async def transform_rdf_upload(
    file: UploadFile = File(..., description="RDF file (JSON-LD or Turtle)"),
    serialization: Literal["jsonld", "turtle"] = Form(..., description="Output format"),
    fuzzy: bool = Form(False, description="Enable fuzzy matching"),
    fuzzy_threshold: int = Form(90, description="Fuzzy threshold 0-100"),
) -> Response:
    try:
        data = await file.read()
        if not data:
            return Response(content="Uploaded file is empty", status_code=400)
        serialized, media_type = _transform_bytes(
            data, file.content_type or "", serialization, fuzzy, fuzzy_threshold
        )
        return Response(content=serialized, media_type=media_type)
    except Exception as e:  # pragma: no cover
        logging.exception("Transformation failed")
        return Response(content=str(e), status_code=400)

