# Prompt template for text2sparql

def generate_prompt(user_question, examples, onto_context) -> str:
    prompt =  f"""You are a RDF expert, and your task is to convert the following natural language query into a SPARQL query. The SPARQL query should be valid and executable on the given ontology.

User question:
{user_question}

You may find the following ontology useful when generating the query:
{onto_context}

Alway include this prefix sockg: <https://idir.uta.edu/sockg-ontology/docs/> in your query.
Reasoning first, specifically, you should first identify the relevant classes and properties in the ontology that are related to the user question. Then, you should construct a valid path complied with the ontology. Finally, you should generate the SPARQL query based on the identified classes and properties.
Finally, put the generated query inside a <sparql> </sparql> tags.
    """.format(
        user_question=user_question,
        examples=examples,
        onto_context=onto_context
    )
    return prompt


# Extract sparql query from the generated text
def extract_sparql_query(text):
    start_tag = "<sparql>"
    end_tag = "</sparql>"
    start_index = text.find(start_tag) + len(start_tag)
    end_index = text.find(end_tag)
    if start_index == -1 or end_index == -1:
        return None
    return text[start_index:end_index].strip()
