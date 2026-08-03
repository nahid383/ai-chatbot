"""
User model.

Design decision: students CANNOT self-register (per your requirement -
only the CR/admin creates accounts). So there's no "signup" endpoint at
all - only /admin/students (create) and /auth/login.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(String, unique=True, nullable=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.student)
    created_at = Column(DateTime, default=datetime.utcnow)
