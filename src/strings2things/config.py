import argparse

def config_args():
    parser = argparse.ArgumentParser(
        description="Convert between strings and ontology terms."
    )
    parser.add_argument(
        "direction", choices=["string2thing", "thing2string"], help="Conversion direction"
    )
    parser.add_argument(
        "--ontology", required=True, help="Path to ontology files directory"
    )
    parser.add_argument(
        "--kg", required=True, help="Path to knowledge graph files directory"
    )
    parser.add_argument(
        "--ontology-uri",
        default="https://imaging-plaza.epfl.ch/ontology#",
        help="Named graph URI for ontology",
    )
    parser.add_argument(
        "--kg-uri",
        default="https://imaging-plaza.epfl.ch/finalGraph",
        help="Named graph URI for knowledge graph",
    )
    parser.add_argument(
        "-o", "--output", default="output.ttl", help="Output file for the converted graph"
    )
    args = parser.parse_args()

    return args
