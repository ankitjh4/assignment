"""
FastAPI dependencies for DRINKOO API.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Optional
from backend.auth import verify_token, TokenData, get_user_by_id


class HTTPAuthCredentials:
    def __init__(self, scheme: str, credentials: str):
        self.scheme = scheme
        self.credentials = credentials


security = HTTPBearer()


async def get_current_user(credentials = Depends(security)) -> TokenData:
    """Dependency to get authenticated user."""
    token = credentials.credentials
    
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return token_data


async def get_current_user_optional(
    credentials = Depends(security)
) -> Optional[TokenData]:
    """Dependency to get user if authenticated (optional)."""
    if credentials is None:
        return None
    
    token = credentials.credentials
    return verify_token(token)
