import os
import glob
import argparse
import rdflib
from config import args
from strings2things.sparql import (
    strings_to_things_query,
    things_to_strings_query
)


def load_graphs_from_path(path, graph, file_extension="*.ttl", format="turtle"):
    """
    Load all RDF files from a given path into the provided graph.
    """
    for file_path in glob.glob(os.path.join(path, file_extension)):
        print(f"Processing file: {file_path}")
        graph.parse(file_path, format=format)
    print(f"Loaded {len(graph)} triples from {path}.")


def initialize_graphs(ontology_path, kg_path, ontology_uri, kg_uri):
    """
    Load and return ontology and knowledge graphs inside a shared dataset.
    """
    dataset = rdflib.Dataset()

    # Load KG
    knowledge_graph = dataset.graph(kg_uri)
    load_graphs_from_path(kg_path, knowledge_graph)

    # Load ontology
    ontology_graph = dataset.graph(ontology_uri)
    load_graphs_from_path(ontology_path, ontology_graph)

    return dataset


def strings_to_things(dataset, output_file="subgraph.ttl"):
    """
    Replace human-readable strings in the KG with ontology IRIs based on matches.
    """
    results = dataset.query(strings_to_things_query)
    new_graph = rdflib.Graph()

    for triple in results.graph:
        new_graph.add(triple)

    new_graph.serialize(destination=output_file, format="turtle")
    print(f"Strings replaced with IRIs and written to {output_file} ({len(new_graph)} triples).")


def things_to_strings(dataset, output_file="output.ttl"):
    """
    Replace IRIs in the KG with human-readable labels using the ontology.
    """
    results = dataset.query(things_to_strings_query)

    new_graph = rdflib.Graph()
    for triple in results.graph:
        new_graph.add(triple)

    new_graph.serialize(destination=output_file, format="turtle")
    print(f"IRIs replaced with labels and written to {output_file} ({len(new_graph)} triples).")


def main():
    parser = argparse.ArgumentParser(description="Convert between strings and ontology terms.")
    parser.add_argument("direction", choices=["string2thing", "thing2string"], help="Conversion direction")
    parser.add_argument("--ontology", required=True, help="Path to ontology files directory")
    parser.add_argument("--kg", required=True, help="Path to knowledge graph files directory")
    parser.add_argument("--ontology-uri", default="https://imaging-plaza.epfl.ch/ontology#", help="Named graph URI for ontology")
    parser.add_argument("--kg-uri", default="https://imaging-plaza.epfl.ch/finalGraph", help="Named graph URI for knowledge graph")
    args = parser.parse_args()

    dataset = initialize_graphs(args.ontology, args.kg, args.ontology_uri, args.kg_uri)

    if args.direction == "string2thing":
        strings_to_things(dataset)
    elif args.direction == "thing2string":
        things_to_strings(dataset)


if __name__ == "__main__":
    main()
