import logging
from fastapi import APIRouter, HTTPException, status

from Backend.models.user import UserCreate, UserLogin, UserOut, Token
from Backend.services import auth_service, db_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate):
    existing = db_service.execute_one(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (payload.username, payload.email),
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    password_hash = auth_service.hash_password(payload.password)
    user_id = db_service.execute_write(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (payload.username, payload.email, password_hash),
    )
    user = db_service.execute_one("SELECT * FROM users WHERE id = ?", (user_id,))
    logger.info("New user signed up: %s", payload.username)
    return UserOut(**user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin):
    user = db_service.execute_one(
        "SELECT * FROM users WHERE username = ?", (payload.username,)
    )
    if not user or not auth_service.verify_password(payload.password, user["password_hash"]):
        logger.warning("Failed login attempt for username: %s", payload.username)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = auth_service.create_access_token(
        {"sub": user["username"], "user_id": user["id"]}
    )
    logger.info("User logged in: %s", payload.username)
    return Token(access_token=token)


@router.post("/logout")
def logout():
    # JWT is stateless; client discards token
    return {"message": "Logged out successfully"}
