"""
Configuration module for DRINKOO application.
Loads settings from environment variables with sensible defaults.
"""
import os
from typing import Optional

class Config:
    """Application configuration."""
    
    # API Settings
    API_TITLE = "DRINKOO RAG Chatbot API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "SKU management and RAG-powered chatbot for DRINKOO beverages"
    
    # Environment
    ENV = os.getenv("ENV", "development")
    DEBUG = ENV == "development"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "Database/drinkoo.db")
    
    # OpenRouter API
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistral-7b-instruct")  # Free model
    
    # File Upload Settings
    MAX_UPLOAD_SIZE_MB = 5
    MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    
    # JWT/Auth
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/drinkoo.log")
    
    # RAG Settings
    RAG_CONTEXT_LIMIT = 3  # Number of support articles to retrieve
    RAG_SCORE_THRESHOLD = 0.3  # Relevance threshold for retrieval
    
    # CORS
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """Validate critical configuration."""
        if not cls.OPENROUTER_API_KEY:
            return False, "OPENROUTER_API_KEY not set in environment"
        
        if not os.path.exists(cls.DATABASE_URL):
            return False, f"Database not found at {cls.DATABASE_URL}. Run: python scripts/load_data.py"
        
        return True, None


# Create upload directory if it doesn't exist
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)
