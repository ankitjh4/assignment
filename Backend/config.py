import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

DATABASE_PATH = os.getenv("DATABASE_PATH", "Database/drinkoo.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))  # 5 MB

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
