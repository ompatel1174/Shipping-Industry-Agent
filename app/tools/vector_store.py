import chromadb
from app.schema_registry import TABLE_SCHEMAS, get_schema_text, get_ddl_context


_CLIENT = None
_COLLECTIONS = {}

PERSIST_DIR = "chroma_db"


def _get_collection(collection_name: str):
    """Lazily initialize the ChromaDB client and a collection."""
    global _CLIENT, _COLLECTIONS
    if _CLIENT is None:
        _CLIENT = chromadb.PersistentClient(path=PERSIST_DIR)
    
    if collection_name not in _COLLECTIONS:
        _COLLECTIONS[collection_name] = _CLIENT.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        if collection_name == "table_schemas":
            _load_schemas(_COLLECTIONS[collection_name])
            
    return _COLLECTIONS[collection_name]


def _load_schemas(collection):
    """Upsert all table schemas into the vector collection."""
    ids = []
    documents = []
    metadatas = []

    for schema in TABLE_SCHEMAS:
        ids.append(schema["table_name"])
        documents.append(get_schema_text(schema))
        metadatas.append({
            "table_name": schema["table_name"],
            "columns": ", ".join(col["name"] for col in schema["columns"]),
        })

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)


def search(query: str, top_k: int = 2) -> list[dict]:
    """
    Perform semantic search against stored table schemas.

    Returns a list of dicts with keys:
        - table_name: name of the matched table
        - schema_text: full schema description
        - ddl: DDL-style CREATE TABLE statement
        - score: distance score (lower = more relevant)
    """
    collection = _get_collection("table_schemas")
    results = collection.query(query_texts=[query], n_results=top_k)

    matched = []
    for i, doc in enumerate(results["documents"][0]):
        table_name = results["metadatas"][0][i]["table_name"]
        schema = next(s for s in TABLE_SCHEMAS if s["table_name"] == table_name)
        matched.append({
            "table_name": table_name,
            "schema_text": doc,
            "ddl": get_ddl_context(schema),
            "score": results["distances"][0][i] if results.get("distances") else None,
        })

    return matched


def upsert_agent_docs(ids, documents, metadatas):
    """Upsert agent documentation chunks into the agent_docs collection."""
    collection = _get_collection("agent_docs")
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)


def search_agent_docs(query: str, top_k: int = 3) -> list[dict]:
    """Search for relevant agent documentation."""
    collection = _get_collection("agent_docs")
    results = collection.query(query_texts=[query], n_results=top_k)
    
    matched = []
    if results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            matched.append({
                "content": doc,
                "metadata": results["metadatas"][0][i],
                "score": results["distances"][0][i] if results.get("distances") else None,
            })
    return matched
