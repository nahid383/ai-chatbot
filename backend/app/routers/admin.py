"""
Admin-only endpoints: upload documents, create student accounts,
review the unknown question queue. All routes here require the
require_admin dependency - a student JWT gets a 403, not a 401,
since they ARE authenticated, just not authorized for this.
"""

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.core.deps import require_admin
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.unknown_question import UnknownQuestion
from app.schemas.document import DocumentOut
from app.schemas.user import UserOut, CreateStudentRequest
from app.services.ingestion_service import ingest_document

router = APIRouter(prefix="/admin", tags=["admin"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@router.post("/upload", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    course_code: str | None = Form(None),
    doc_type: str = Form("general"),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: {ALLOWED_EXTENSIONS}",
        )

    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    stored_filename = f"{uuid.uuid4()}{suffix}"
    stored_path = Path(settings.UPLOAD_DIR) / stored_filename

    with stored_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        original_filename=file.filename,
        stored_filename=stored_filename,
        course_code=course_code,
        doc_type=doc_type,
        uploaded_by=_admin.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Synchronous for now (see ingestion_service docstring re: background tasks).
    ingest_document(db, document, str(stored_path))
    db.refresh(document)

    return document


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.post("/students", response_model=UserOut)
def create_student(
    payload: CreateStudentRequest,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    student = User(
        student_id=payload.student_id,
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.temporary_password),
        role=UserRole.student,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/unknown-questions")
def list_unknown_questions(
    db: Session = Depends(get_db), _admin: User = Depends(require_admin)
):
    questions = (
        db.query(UnknownQuestion)
        .filter(UnknownQuestion.resolved == False)  # noqa: E712
        .order_by(UnknownQuestion.created_at.desc())
        .all()
    )
    return [
        {"id": q.id, "question": q.question, "created_at": q.created_at}
        for q in questions
    ]
