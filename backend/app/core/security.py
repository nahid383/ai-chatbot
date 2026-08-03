"""
Password hashing and JWT creation/verification.

Why we NEVER store plain-text passwords: if your database is ever
leaked (misconfigured backup, SQL injection, etc.), plain-text
passwords hand attackers everything immediately. Hashing with bcrypt
is one-way - even you, the admin, can't "look up" a student's password,
only verify a guess against the stored hash.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, role: str) -> str:
    """
    Creates a JWT containing the user's id (subject) and role, signed
    with our secret key. The role is embedded so we can authorize
    admin-only endpoints without an extra database lookup on every
    request (a small but real performance win, standard practice).
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None
