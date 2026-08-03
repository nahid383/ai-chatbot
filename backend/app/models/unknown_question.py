"""
UnknownQuestion model - implements the "Unknown Question Queue" feature.
Whenever the RAG pipeline can't find a confident answer (Lesson 6:
retrieval confidence thresholding), the question lands here for the
admin/CR to review and answer manually, growing the knowledge base.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class UnknownQuestion(Base):
    __tablename__ = "unknown_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question = Column(Text, nullable=False)
    asked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved = Column(Boolean, default=False)
    admin_note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
