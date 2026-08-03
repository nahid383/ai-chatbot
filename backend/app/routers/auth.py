from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.schemas.user import UserOut
from app.core.security import verify_password, create_access_token
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Uses the standard OAuth2 "password" flow shape (form-encoded
    username/password) instead of a custom JSON body. Two concrete
    reasons:
    1. It's what Swagger's built-in "Authorize" button expects and
       POSTs to automatically - so /docs auth actually works.
    2. It matches FastAPI's documented convention, which anyone else
       reading this code will recognize immediately.

    Note: OAuth2PasswordRequestForm's field is always called
    "username" even though we're treating it as the user's email.
    That's a fixed field name from the OAuth2 spec, not our choice.
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    # Deliberately identical error for "no such user" and "wrong password" -
    # this prevents an attacker from using the error message to figure out
    # which emails are registered students (a real, common vulnerability).
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
    )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise invalid_credentials

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Lets the frontend ask "who am I / what's my role" right after login,
    so it can route admins to the admin dashboard and students to chat -
    without decoding the JWT itself on the client (keeps that logic
    server-side, where it belongs).
    """
    return current_user
