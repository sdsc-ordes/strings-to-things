from typing import Dict


def append_input_term(
    input_dict: Dict, original: str, predicate: str, suggested_iri: str
):
    """
    Format the input term for the LLM.
    """
    # Check if the suggested IRI is not null
    if suggested_iri:
        # Add the term to the input dictionary
        input_dict[original] = {"predicate": predicate, "suggestedIRI": suggested_iri}
    else:
        # Add the term without a suggested IRI
        input_dict[original] = {"predicate": predicate, "suggestedIRI": None}
