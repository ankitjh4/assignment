"""Application configuration — reads from environment variables only."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# JWT
SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me-in-production-use-a-long-random-string")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Database
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{Path(__file__).parent / 'drinkoo.db'}",
)

# OpenRouter
OPENROUTER_API_KEY: str = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL: str = os.environ.get("OPENROUTER_MODEL", "liquid/lfm-2.5-1.2b-instruct:free")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

# Upload
UPLOAD_DIR: Path = Path(__file__).parent / "uploads"
ALLOWED_IMAGE_TYPES: set[str] = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_UPLOAD_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB

# App
APP_VERSION: str = "1.0.0"
APP_ENV: str = os.environ.get("APP_ENV", "development")
