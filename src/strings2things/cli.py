import os
import glob
import argparse
import rdflib
from .config import config_args
from .queries import get_strings_to_things_query, get_things_to_strings_query


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


def strings_to_things(dataset: str, output_file:str, kg_uri:str, ontology_uri:str):
    """
    Replace human-readable strings in the KG with ontology IRIs based on matches.
    """
    strings_to_things_query = get_strings_to_things_query(kg_uri, ontology_uri)
    results = dataset.query(strings_to_things_query)
    new_graph = rdflib.Graph()

    for triple in results.graph:
        new_graph.add(triple)

    new_graph.serialize(destination=output_file, format="turtle")
    print(
        f"Strings replaced with IRIs and written to {output_file} ({len(new_graph)} triples)."
    )


def things_to_strings(dataset:str, output_file:str, kg_uri:str, ontology_uri:str):
    """
    Replace IRIs in the KG with human-readable labels using the ontology.
    """
    things_to_strings_query = get_things_to_strings_query(kg_uri, ontology_uri)
    results = dataset.query(things_to_strings_query)

    new_graph = rdflib.Graph()
    for triple in results.graph:
        new_graph.add(triple)

    new_graph.serialize(destination=output_file, format="turtle")
    print(
        f"IRIs replaced with labels and written to {output_file} ({len(new_graph)} triples)."
    )


def main():

    args = config_args()

    if args.direction == "string2thing":
        dataset = initialize_graphs(args.ontology, args.kg, args.ontology_uri, args.kg_uri)
        strings_to_things(dataset, args.output_file, args.kg_uri, args.ontology_uri)
    elif args.direction == "thing2string":
        dataset = initialize_graphs(args.ontology, args.kg, args.ontology_uri, args.kg_uri)
        things_to_strings(dataset, args.output_file, args.kg_uri, args.ontology_uri)
    else:
        print("Invalid direction. Please choose from: string2thing, thing2string, or api.")

if __name__ == "__main__":
    main()