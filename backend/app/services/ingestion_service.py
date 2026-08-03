"""
The full ingestion pipeline (Lessons 2-4, wired together):
extract text -> chunk -> embed each chunk -> store in ChromaDB
with metadata linking back to the PostgreSQL Document row.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.services.text_extraction import extract_text
from app.services.chunking_service import chunk_text
from app.services.llm_service import embed_text
from app.services import vector_store


def ingest_document(db: Session, document: Document, file_path: str) -> None:
    """
    Runs synchronously for simplicity in this milestone. In production,
    with larger files or higher upload volume, this would move to a
    background task queue (e.g. Celery, or FastAPI's BackgroundTasks
    at minimum) so the admin's upload request returns instantly instead
    of waiting for the full pipeline. Flagging this as a clear
    "next improvement," not doing it now to avoid premature complexity.
    """
    document.status = DocumentStatus.processing
    db.commit()

    try:
        raw_text = extract_text(file_path)
        if not raw_text.strip():
            raise ValueError("No extractable text found in this file.")

        chunks = chunk_text(raw_text)
        if not chunks:
            raise ValueError("Chunking produced no usable chunks.")

        chunk_ids = [f"{document.id}_{i}" for i in range(len(chunks))]
        embeddings = [embed_text(c, task_type="RETRIEVAL_DOCUMENT") for c in chunks]
        metadatas = [
            {
                "document_id": str(document.id),
                "course_code": document.course_code or "",
                "doc_type": document.doc_type,
                "source_filename": document.original_filename,
            }
            for _ in chunks
        ]

        vector_store.add_chunks(
            chunk_ids=chunk_ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )

        document.status = DocumentStatus.processed
        document.error_message = None

    except Exception as exc:  # noqa: BLE001 - we deliberately catch broadly here
        document.status = DocumentStatus.failed
        document.error_message = str(exc)

    db.commit()
