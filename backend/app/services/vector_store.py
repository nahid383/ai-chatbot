"""
Thin wrapper around ChromaDB (Lesson 4). Using PersistentClient means
Chroma runs embedded in this same process and writes to a local folder
on disk (CHROMA_PERSIST_DIR) - no separate database server needed,
which is exactly right for a project this size.
"""

import chromadb

from app.config import settings

_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

# One collection for all document chunks. We rely on metadata filtering
# (course_code, doc_type, document_id) rather than separate collections
# per course - simpler to manage, and Chroma's `where` filter handles
# this cleanly (Lesson 4: metadata filtering).
_collection = _client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"},  # explicit: use cosine distance
)


def add_chunks(
    chunk_ids: list[str],
    embeddings: list[list[float]],
    documents: list[str],
    metadatas: list[dict],
) -> None:
    # upsert() (not add()) deliberately: add() silently skips - and can
    # leave inconsistent/partial state for - IDs that already exist.
    # upsert() cleanly inserts new chunks or overwrites existing ones,
    # which matters whenever a document gets re-processed.
    _collection.upsert(
        ids=chunk_ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )


def delete_document_chunks(document_id: str) -> None:
    """Used when re-processing or removing a document (knowledge versioning)."""
    _collection.delete(where={"document_id": document_id})


def query(
    query_embedding: list[float],
    top_k: int,
    course_code: str | None = None,
) -> dict:
    where_filter = {"course_code": course_code} if course_code else None
    return _collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
    )
