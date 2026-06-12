"""Password hashing and JWT issuance for DRINKOO.

Uses bcrypt via passlib for password hashing (never stored in plaintext).
Issues short-lived JWTs and reads them from an HttpOnly cookie.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import jwt

from .config import get_settings

SETTINGS = get_settings()
ALG = SETTINGS.jwt_algorithm
COOKIE_NAME = "drinkoo_session"


def hash_password(password: str) -> str:
    if not isinstance(password, str) or not password:
        raise ValueError("password must be a non-empty string")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    if not password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, role: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=SETTINGS.jwt_exp_hours)).timestamp()),
    }
    return jwt.encode(payload, SETTINGS.app_secret, algorithm=ALG)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, SETTINGS.app_secret, algorithms=[ALG])
    except jwt.PyJWTError:
        return None


def validate_password_strength(password: str) -> Optional[str]:
    """Return a human-readable reason if the password is too weak, else None."""
    if not password or len(password) < 8:
        return "Password must be at least 8 characters."
    if password.lower() == password:
        return "Password must include at least one uppercase letter."
    if password.upper() == password:
        return "Password must include at least one lowercase letter."
    if not any(ch.isdigit() for ch in password):
        return "Password must include at least one digit."
    return None
