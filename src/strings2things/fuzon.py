from pyfuzon.matcher import TermMatcher

def extract_relevant_terms(ontology, query, n=5):
    """
    Extract relevant terms from a list of terms based on a query string.
    
    :param terms: List of terms to search through.
    :param query: Query string to match against the terms.
    :param n: Number of top matches to return.
    :return: List of tuples containing the matched term and its score.
    """
    matcher = TermMatcher.from_files([ontology])
    return matcher.top(query, n)

