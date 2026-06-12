"""Signup, login, logout, and current-user endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from ..deps import get_db, require_user
from ..logging_config import get_logger
from ..models import User
from ..security import (
    COOKIE_NAME,
    create_access_token,
    hash_password,
    validate_password_strength,
    verify_password,
)
from ..config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])
log = get_logger("drinkoo.auth")
settings = get_settings()


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=80)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserPublic(BaseModel):
    id: int
    email: str
    full_name: str
    role: str


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.environment.lower() not in {"local", "test"},
        max_age=settings.jwt_exp_hours * 3600,
        path="/",
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
def signup(payload: SignupRequest, response: Response, db: Session = Depends(get_db)) -> UserPublic:
    weakness = validate_password_strength(payload.password)
    if weakness:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=weakness)

    existing = db.query(User).filter(User.email == payload.email.lower()).one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role="customer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role, user.email)
    _set_session_cookie(response, token)

    log.info("user_signup", extra={"user_id": user.id, "email": user.email})
    return UserPublic(id=user.id, email=user.email, full_name=user.full_name, role=user.role)


@router.post("/login", response_model=UserPublic)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> UserPublic:
    user = db.query(User).filter(User.email == payload.email.lower()).one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")

    token = create_access_token(user.id, user.role, user.email)
    _set_session_cookie(response, token)
    log.info("user_login", extra={"user_id": user.id})
    return UserPublic(id=user.id, email=user.email, full_name=user.full_name, role=user.role)


@router.post("/logout")
def logout(response: Response) -> dict:
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(require_user)) -> UserPublic:
    return UserPublic(id=user.id, email=user.email, full_name=user.full_name, role=user.role)
