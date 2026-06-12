"""Application configuration loaded from environment / .env file.

Secrets must never be hard-coded. The OpenRouter free model name is fixed at
`nvidia/nemotron-3-ultra-550b-a55b:free` and is also published in `prompt.md`.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Runtime configuration. Reads from the project `.env` if present."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "DRINKOO"
    app_version: str = "1.0.0"
    environment: str = "local"

    app_secret: str = "dev-only-secret-change-me-in-production-please-32+chars"
    jwt_algorithm: str = "HS256"
    jwt_exp_hours: int = 24

    db_url: str = f"sqlite:///{(PROJECT_ROOT / 'Database' / 'drinkoo.db').as_posix()}"

    upload_dir: str = str(PROJECT_ROOT / "uploads")
    max_upload_mb: int = 5

    openrouter_api_key: str = ""
    openrouter_model: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_timeout_seconds: int = 30

    allowed_origins: str = "http://localhost:8000,http://127.0.0.1:8000"

    log_file_path: str = "./logs/drinkoo.log"
    log_file_max_mb: int = 5
    log_file_backup_count: int = 5

    testing: bool = False

    @field_validator("openrouter_model")
    @classmethod
    def _pin_model(cls, value: str) -> str:
        return value or "nvidia/nemotron-3-ultra-550b-a55b:free"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def has_openrouter_key(self) -> bool:
        key = (self.openrouter_api_key or "").strip()
        return bool(key) and not key.startswith("replace_with")

    @property
    def upload_dir_path(self) -> Path:
        path = Path(self.upload_dir)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path

    @property
    def project_root(self) -> Path:
        return PROJECT_ROOT


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
