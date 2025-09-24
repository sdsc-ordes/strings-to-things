"""Command Line Interface for strings2things.

Provides:
  - `strings2things serve` : Run the FastAPI application (uvicorn)
  - `strings2things transform` : Transform an RDF input file (Turtle or JSON-LD)

Installation (editable):
    uv pip install -e .

Examples:
    strings2things serve --host 0.0.0.0 --port 8080
    strings2things transform --input data.ttl --serialization jsonld --output out.jsonld

Environment:
  Ontology loading relies on environment variables (see config). Use `--no-ontology`
  to run transformation without loading ontologies.
"""
from __future__ import annotations

import json
import sys
import typer
import uvicorn
from pathlib import Path
from typing import Optional, Literal

from strings2things.app.core.ontology_manager import OntologyManager
from strings2things.app.core.rdf_transformer import RDFTransformer
from strings2things.app.utils.rdf_utils import parse_rdf, serialize_rdf

app = typer.Typer(help="CLI tools for the strings2things RDF transformer")


def _load_label_map(disable: bool) -> dict[str, str]:
    if disable:
        return {}
    manager = OntologyManager()
    try:
        manager.load_ontologies()
    except Exception as e:  # pragma: no cover - resilience path
        typer.echo(f"[warn] Ontology load failed: {e}", err=True)
        return {}
    return manager.get_label_map() or {}


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", help="Host interface"),
    port: int = typer.Option(8000, help="Port to bind"),
    reload: bool = typer.Option(False, help="Enable uvicorn reload (dev only)"),
    log_level: str = typer.Option("info", help="Uvicorn log level"),
):
    """Run the FastAPI application via uvicorn."""
    uvicorn.run(
        "strings2things.app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )


@app.command()
def transform(
    input: Path = typer.Option(..., exists=True, dir_okay=False, readable=True, help="Input RDF file (Turtle or JSON-LD)"),
    serialization: Literal["jsonld", "turtle"] = typer.Option(
        ..., "--serialization", "-s", help="Output serialization format"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path (stdout if omitted)"
    ),
    fuzzy: bool = typer.Option(False, help="Enable fuzzy label matching"),
    fuzzy_threshold: int = typer.Option(90, min=0, max=100, help="Fuzzy threshold 0-100"),
    no_ontology: bool = typer.Option(
        False, help="Disable ontology loading (use empty label map)"
    ),
):
    """Transform an RDF graph from a local file and emit the result."""
    data = input.read_bytes()
    # Simple format inference
    first = data.lstrip()[:1]
    if first in (b"{", b"["):
        in_format = "json-ld"
    else:
        in_format = "turtle"

    graph = parse_rdf(data, format=in_format)
    label_map = _load_label_map(disable=no_ontology)
    transformer = RDFTransformer(label_map, fuzzy=fuzzy, fuzzy_threshold=fuzzy_threshold)
    transformed = transformer.transform(graph)
    out_fmt = "json-ld" if serialization == "jsonld" else "turtle"
    serialized = serialize_rdf(transformed, output_format=out_fmt)

    if output:
        output.write_text(serialized, encoding="utf-8")
    else:
        typer.echo(serialized)


def main():  # legacy entry point if needed
    app()

if __name__ == "__main__":  # pragma: no cover
    main()
