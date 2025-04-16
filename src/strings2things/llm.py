from prompt import match_terms_prompt
from pydantic import BaseModel
from openai import OpenAI
import json


class Item(BaseModel):
    exists: bool
    iri: str


class Response(BaseModel):
    __root__: list[Item]


client = OpenAI()


def generate_prompt(prompt: str, rdf_enums: str):
    return prompt + "\n\n" + "[RDF ENUM]\n" + rdf_enums + "\n\n" + "[INPUT]"


def query_llm(rdf_enums: str, input_query: str):
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": generate_prompt(match_terms_prompt, rdf_enums),
            },
            {"role": "user", "content": input_query},
        ],
        response_format=Response,
    )
    return json.loads(completion.choices[0].message.content)
