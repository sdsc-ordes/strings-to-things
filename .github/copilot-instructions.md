# AI Coding Agent Instructions - strings-to-things

## Project Overview
This is an RDF transformation microservice that converts string literals in knowledge graphs to structured IRIs using ontology mappings. The service loads ontologies from SPARQL endpoints and performs exact/fuzzy matching to replace text values with semantic identifiers.

## Key Architecture Components

### Core RDF Transformation Flow
- `OntologyManager` loads ontologies from GraphDB via SPARQL CONSTRUCT queries
- Builds label maps: `{lowercase_label -> IRI}` from `rdfs:label` and `skos:prefLabel` 
- `RDFTransformer` processes input RDF graphs, replacing matching literals with IRIs
- FastAPI endpoints accept RDF uploads and return transformed graphs

### Critical Patterns

**Ontology Loading**: Always load from named graphs using SPARQL CONSTRUCT:
```python
CONSTRUCT { ?s ?p ?o }
WHERE { GRAPH <{graph_iri}> { ?s ?p ?o } }
```

**Label Normalization**: All labels are `.strip().lower()` for consistent matching
**Ambiguity Handling**: Duplicate labels across IRIs are detected and excluded from label maps
**Fuzzy Matching**: Uses RapidFuzz with configurable thresholds (default: 90)

## Development Workflows

### Build & Run Commands
```bash
just setup          # Initial project setup
just develop         # Enter Nix dev shell
just run [args]      # Execute CLI with uv
just format          # Format code with treefmt
just notebook        # Start Jupyter notebook
uv build --out-dir .output/build  # Build package
```

### Testing Patterns
- Test with `pytest` using RDFLib Graph fixtures
- Mock SPARQL endpoints for ontology loading tests
- Test both exact and fuzzy matching scenarios in `test_rdf_transformer.py`

### Configuration Management
Settings via Pydantic with `.env` file:
- `ONTOLOGY_SPARQL_ENDPOINT`: GraphDB endpoint URL
- `ONTOLOGY_GRAPH_IRIS`: Comma-separated named graph URIs
- `GRAPHDB_USERNAME/PASSWORD`: Authentication
- `FAIL_ON_AMBIGUOUS_LABELS`: Boolean for strict validation

## Project-Specific Conventions

### RDF Handling
- Use RDFLib for all RDF operations
- Preserve original triples when adding transformed versions
- Add provenance with `thingOf` predicate linking IRI to original literal
- Support multiple serialization formats via FastAPI form parameters

### Error Handling
- Validate ontology loading with comprehensive logging
- Handle SPARQL connection failures gracefully
- Log all transformation decisions with `TransformationLog`

### File Structure
```
src/strings2things/app/
├── main.py              # FastAPI app entry point
├── config.py            # Pydantic settings
├── api/endpoints.py     # REST API routes
├── core/
│   ├── ontology_manager.py    # SPARQL loading & label mapping
│   ├── rdf_transformer.py     # Core transformation logic
│   └── transformation_log.py   # Audit trail
└── utils/rdf_utils.py   # RDF parsing/serialization
```

### Dependencies
- Uses `uv` for Python package management
- RDF: `rdflib`, `SPARQLWrapper`
- Web: `fastapi`, `python-multipart` 
- Fuzzy matching: `rapidfuzz`
- Validation: `pydantic`, `pydantic-settings`

### Nix Integration
Project uses Nix flakes for reproducible environments. All commands should run through `just` which wraps Nix development shells. The `justfile` contains the canonical build/test/format commands.

## Key Implementation Notes
- Ontologies define enumeration classes with `rdfs:label` values for matching
- The imaging ontology (`examples/ontologies/ontology.ttl`) shows the expected structure
- Fuzzy matching is optional and configurable per-request
- All transformations preserve backward compatibility by keeping original triples