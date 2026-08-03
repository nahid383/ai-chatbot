"""
ChatMessage model - stores conversation history per user, grouped by
session_id. This backs the "sliding window" memory strategy from
Lesson 6: we fetch the last N messages for a session_id to build
conversation context for the LLM.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)  # JSON-encoded list of source filenames
    created_at = Column(DateTime, default=datetime.utcnow)
