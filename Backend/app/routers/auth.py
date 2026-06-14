"""
Authentication routes for DRINKOO API.
Handles signup, login, logout.
"""
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.auth import (
    UserCredentials, User, create_user, authenticate_user,
    create_access_token
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: User


@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest):
    """Create new user account."""
    try:
        # Validate input
        if len(request.username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters"
            )
        
        if len(request.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters"
            )
        
        if "@" not in request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Create user
        credentials = UserCredentials(
            username=request.username,
            email=request.email,
            password=request.password
        )
        
        user = create_user(credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Create token
        token, _ = create_access_token(user.id, user.username)
        
        logger.info(f"User signup successful: {user.username}")
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return token."""
    try:
        user = authenticate_user(request.username, request.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        token, _ = create_access_token(user.id, user.username)
        
        logger.info(f"User login successful: {user.username}")
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=user
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout():
    """Logout user (client-side token deletion)."""
    # Token invalidation can be done client-side by deleting the token
    # For enhanced security, could implement token blacklist
    return {"message": "Logged out successfully"}
