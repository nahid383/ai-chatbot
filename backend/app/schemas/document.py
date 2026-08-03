import uuid
from datetime import datetime
from pydantic import BaseModel

from app.models.document import DocumentStatus


class DocumentOut(BaseModel):
    id: uuid.UUID
    original_filename: str
    course_code: str | None
    doc_type: str
    status: DocumentStatus
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True
