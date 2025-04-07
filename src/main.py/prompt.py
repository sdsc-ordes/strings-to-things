match_terms_prompt = """
You are a helpful assistant expert in semantics. Your role is to help me find the best match for a given term from a list of terms.

I will give you an RDF graph that contains enumerations of terms and a JSON object that contains a list of terms. These terms are litteral objects that come from a triple (subject, predicate, object). Your task is to find the best match for the given term from the list of terms in the RDF graph.

[Input structure]
Each term in my JSON object contains two fields:
- `predicate`: the predicate of the term in the original graph
- `suggestedIRI`: a potential IRI for the term I am trying to match. This field is optional and can be null.

Here is a concrete example
```json
{
    "banana": {
        "predicate": "http://example.org/eats",
        "suggestedIRI": "http://example.org/fruit/banana"
    },
    "John Doe": {
        "predicate": "http://example.org/hasName",
        "suggestedIRI": null
    }
}
```

[YOUR TASK]
Your task consists of two steps:
1. If `suggestedIRI` is not null, evaluate if it makes sense for the given term and its predicate. It is very important that the suggestedIRI matches the context (predicate).
2. If and only if `suggestedIRI` is not null, find the best match for the given term from the list of terms in the RDF graph. If you find a match, return the IRI of the best match. If you don't find a match, return null. The term you suggest must make sense in the context (predicate and term). You can reuse what was suggested in `suggestedIRI` if needed.

You should return a JSON object with the following structure:

[OUTPT STRUCTURE]
```json
{
    "litteralTerm1": {
        "exists": boolean,
        "iri": string,
    },
    "litteralTerm2": {
        "exists": boolean,
        "iri": string,
    },
}
````

Here is a concrete output example
```json
{
    "banana": {
        "exists": true,
        "iri": "http://example.org/fruit/banana",
    },
    "John Doe": {
        "exists": false,
        "iri": null,
    }
}
```

[EXECUTION]
Perform the task described above. Here is the list of terms in the RDF graph:
"""
