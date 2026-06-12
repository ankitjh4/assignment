"""FastAPI dependencies: DB session and current user."""
from __future__ import annotations

from typing import Iterator, Optional

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import User
from .security import COOKIE_NAME, decode_token


def get_db() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _extract_token(request: Request, cookie_token: Optional[str]) -> Optional[str]:
    if cookie_token:
        return cookie_token
    auth = request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return auth.split(" ", 1)[1].strip()
    return None


def current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    cookie_token: Optional[str] = Cookie(default=None, alias=COOKIE_NAME),
) -> Optional[User]:
    token = _extract_token(request, cookie_token)
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    try:
        user_id = int(payload.get("sub", "0"))
    except (TypeError, ValueError):
        return None
    if not user_id:
        return None
    return db.get(User, user_id)


def require_user(user: Optional[User] = Depends(current_user_optional)) -> User:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
