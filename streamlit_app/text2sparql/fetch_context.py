from pymongo import MongoClient
from langchain_cohere import CohereEmbeddings
from thefuzz import process
import os

DIMENSION = 1024
DATABASE = "sockg"
ONTO_COLLECTION = "rdf_schema"
VECTOR_SEARCH_INDEX_NAME = "vector_index"

# ToDo: add example queries collection Later
embedding = CohereEmbeddings(
    cohere_api_key=os.getenv('COHERE_API'),
    model=os.getenv('COHERE_MODEL'),
)
mongodb_connection_uri = f"mongodb+srv://{os.getenv('MONGODB_USERNAME')}:{os.getenv('MONGODB_PASSWORD')}@sockg.2gtzn.mongodb.net/?retryWrites=true&w=majority&appName=SOCKG"

client = MongoClient(host=mongodb_connection_uri)
onto_collection = client[DATABASE][ONTO_COLLECTION]


def _ruled_based_classes_search(question, limit=3):
    all_classes = onto_collection.distinct("name")
    matches = process.extract(question, all_classes, limit=limit)
    classes = [match[0] for match in matches]
    rule_based_res = onto_collection.find({"name": {"$in": classes}})
    return [doc['name'] for doc in rule_based_res]

def _semantic_based_classes_search(question, num_candidates = 4, limit=3):
    question_emb = embedding.embed_query(question)
    search_res = onto_collection.aggregate([
    {
        "$vectorSearch": {
        "index": VECTOR_SEARCH_INDEX_NAME,
        "path": "embedding",
        "queryVector": question_emb,
        "numCandidates": num_candidates,
        "limit": limit
        }
    }])
    return [doc['name'] for doc in search_res]


# Shorted path to fetch intermediate node the is neccesary to fetch the final node
def shorted_path(graph, start_node, end_node):
    visited = set()
    queue = [(start_node, [start_node])]
    while queue:
        current_node, path = queue.pop(0)
        if current_node == end_node:
            return path
        visited.add(current_node)
        for neighbor in graph.get(current_node, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    return None

# Fetch graph from the database
def fetch_graph():
    doc = onto_collection.find_one({"name": "graph"})
    return doc['value']


def fetch_ontology_context(query):
    relevant_classes = set()

    # Ruled based search
    relevant_classes.update(_ruled_based_classes_search(query))

    # Semantic based search
    relevant_classes.update(_semantic_based_classes_search(query))

    # Iterate over all pairs of relevant classes
    pairs = [(c1, c2) for i, c1 in enumerate(relevant_classes) for c2 in list(relevant_classes)[i + 1:]]
    # find the shortest path between each pair
    graph = fetch_graph()
    for c1, c2 in pairs:
        path = shorted_path(graph, c1, c2)
        if path:
            relevant_classes.update(path)

    # Convert the set to a list
    relevant_classes = list(relevant_classes)

    # Fetch the summaries of the relevant classes
    docs = onto_collection.find({"name": {"$in": relevant_classes}})

    # Return a dictionary
    res = []
    for doc in docs:
        # Check if the document has the 'name' and 'summary' fields
        if 'name' in doc and 'summary' in doc:    
            res.append({
                "name": doc['name'],
                "summary": doc['summary'],
            })

    return res