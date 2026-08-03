"""
Document model - the PostgreSQL "system of record" for every uploaded
file. This is separate from ChromaDB, which stores the chunked +
embedded content DERIVED from these files (see Lesson 4 recap: two
databases, two jobs).
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class DocumentStatus(str, enum.Enum):
    pending = "pending"        # uploaded, not yet processed
    processing = "processing"  # chunking/embedding in progress
    processed = "processed"    # searchable in chat now
    failed = "failed"          # something went wrong during ingestion


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)  # actual name on disk
    course_code = Column(String, nullable=True, index=True)  # e.g. "CSE331"
    doc_type = Column(String, nullable=False, default="general")
    # doc_type examples: "notice", "routine", "resource", "announcement"
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(SAEnum(DocumentStatus), default=DocumentStatus.pending)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
