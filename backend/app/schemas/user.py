import uuid
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserOut(BaseModel):
    id: uuid.UUID
    student_id: str | None
    full_name: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy object


class CreateStudentRequest(BaseModel):
    student_id: str
    full_name: str
    email: EmailStr
    # Admin sets a temporary password; student can change it later
    # (a "change password" endpoint is a natural next feature to add).
    temporary_password: str
