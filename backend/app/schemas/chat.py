import uuid
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: uuid.UUID | None = None  # None = start a new conversation
    course_code: str | None = None       # optional metadata filter


class SourceOut(BaseModel):
    filename: str
    course_code: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: uuid.UUID
    sources: list[SourceOut]
    was_answered_from_knowledge_base: bool
