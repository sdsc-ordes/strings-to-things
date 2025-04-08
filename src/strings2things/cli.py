from strings2things.format import append_input_term
from strings2things.sparql import enumeration_query, find_matches_query, find_predicate_query
from pyfuzon.matcher import TermMatcher
import os
import json
import rdflib

MATCH_THRESHOLD = 0.8

def main():
    knowledge_graph_path = os.getenv("KNOWLEDGE_GRAPH_PATH")
    ontologies_path = os.getenv("ONTOLOGIES_PATH")

    onto = rdflib.Graph()
    onto.parse(ontologies_path)

    # SPARQLwrapper
    dataset = rdflib.Dataset()

    #FIXME: Is `data` used?
    data = dataset.graph("https://imaging-plaza.epfl.ch/finalGraph")
    data.parse(knowledge_graph_path)
    # Load the knowledge graph

    # todo filter down ontology to only get triples related to enumerations

    # Filter down ontology to only get triples related to enumerations

    enumeration_results = onto.query(enumeration_query)
    # Create a new graph to store the enumeration triples
    enumeration_graph = rdflib.Graph()


    # Add the results of the CONSTRUCT query to the new graph
    for triple in enumeration_results.graph:
        enumeration_graph.add(triple)

    #FIXME: Is `enum` used?
    enum = dataset.graph("https://imaging-plaza.epfl.ch/ontology#enums")
    enum.parse(data=enumeration_graph.serialize(format="turtle"), format="turtle")

    results = dataset.query(find_matches_query)

    # Create a new graph to store the constructed triples
    constructed_graph = rdflib.Graph()

    # Add the results of the CONSTRUCT query to the new graph
    for triple in results.graph:
        constructed_graph.add(triple)


    matcher = TermMatcher.from_files([ontologies_path])

    inputdict = {}
    for term in constructed_graph.query(find_predicate_query):
        searchterm = term[0]
        predicate = term[1]
        if sorted(matcher.score(searchterm), reverse=True)[0] / len(searchterm) > MATCH_THRESHOLD:
            suggestedterm = matcher.top(searchterm, 1)[0]
            print(suggestedterm.uri)
            append_input_term(inputdict, str(searchterm), str(predicate), suggestedterm.uri)
        else :
            append_input_term(inputdict, str(searchterm), str(predicate), None)

    json_input = json.dumps(inputdict)

    print(json_input)

# TODO: create enums list
# TODO: call LLM


if __name__ == "__main__":
    main()
