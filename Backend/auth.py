"""
Authentication utilities for DRINKOO.
Handles password hashing, JWT tokens, and user authentication.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
import sqlite3
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from backend.config import Config
from backend.database import execute_query, execute_insert

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    """User model."""
    id: int
    username: str
    email: str


class TokenData(BaseModel):
    """JWT token payload."""
    username: str
    user_id: int


class UserCredentials(BaseModel):
    """Login/signup credentials."""
    username: str
    email: str
    password: str


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, username: str) -> Tuple[str, datetime]:
    """Create JWT access token."""
    expires_delta = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "user_id": user_id,
        "username": username,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        Config.SECRET_KEY,
        algorithm=Config.ALGORITHM
    )
    
    logger.info(f"Created token for user: {username}")
    return encoded_jwt, expire


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=[Config.ALGORITHM]
        )
        username = payload.get("username")
        user_id = payload.get("user_id")
        
        if username is None or user_id is None:
            return None
        
        return TokenData(username=username, user_id=user_id)
    
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def user_exists(username: str, email: str) -> bool:
    """Check if user already exists."""
    try:
        results = execute_query(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        )
        return len(results) > 0
    except Exception as e:
        logger.error(f"Error checking user existence: {e}")
        return False


def create_user(credentials: UserCredentials) -> Optional[User]:
    """Create new user."""
    if user_exists(credentials.username, credentials.email):
        logger.warning(f"User creation failed: user already exists ({credentials.username})")
        return None
    
    try:
        password_hash = hash_password(credentials.password)
        user_id = execute_insert(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (credentials.username, credentials.email, password_hash)
        )
        
        logger.info(f"User created: {credentials.username} (ID: {user_id})")
        return User(id=user_id, username=credentials.username, email=credentials.email)
    
    except Exception as e:
        logger.error(f"User creation error: {e}")
        return None


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password."""
    try:
        results = execute_query(
            "SELECT id, username, email, password_hash FROM users WHERE username = ?",
            (username,)
        )
        
        if not results:
            logger.warning(f"Login failed: user not found ({username})")
            return None
        
        user_data = results[0]
        
        if not verify_password(password, user_data["password_hash"]):
            logger.warning(f"Login failed: invalid password ({username})")
            return None
        
        logger.info(f"User authenticated: {username}")
        return User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"]
        )
    
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[User]:
    """Get user by ID."""
    try:
        results = execute_query(
            "SELECT id, username, email FROM users WHERE id = ?",
            (user_id,)
        )
        
        if not results:
            return None
        
        user_data = results[0]
        return User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"]
        )
    
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return None
