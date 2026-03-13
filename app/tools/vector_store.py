"""
Tool 1 – Table Schema Vector Storage Tool

Stores database table schemas in a ChromaDB vector database and enables
semantic search to retrieve the most relevant table schema for a user query.
"""

import chromadb
from app.schema_registry import TABLE_SCHEMAS, get_schema_text, get_ddl_context


_CLIENT = None
_COLLECTION = None

COLLECTION_NAME = "table_schemas"
PERSIST_DIR = "chroma_db"


def initialize():
    """Ensure the ChromaDB client and collection are ready and loaded."""
    global _CLIENT, _COLLECTION
    if _COLLECTION is None:
        _CLIENT = chromadb.PersistentClient(path=PERSIST_DIR)
        _COLLECTION = _CLIENT.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        _load_schemas()
    return _COLLECTION


def _load_schemas():
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

    _COLLECTION.upsert(ids=ids, documents=documents, metadatas=metadatas)


def search(query: str, top_k: int = 2) -> list[dict]:
    """
    Perform semantic search against stored table schemas.

    Returns a list of dicts with keys:
        - table_name: name of the matched table
        - schema_text: full schema description
        - ddl: DDL-style CREATE TABLE statement
        - score: distance score (lower = more relevant)
    """
    collection = initialize()
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
