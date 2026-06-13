from pydantic import BaseModel, field_validator
from typing import Optional
import re


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email address format")
        return v.lower()


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
