from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = answer_question(
        db=db,
        user_id=current_user.id,
        question=payload.message,
        session_id=payload.session_id,
        course_code=payload.course_code,
    )
    return ChatResponse(**result)
