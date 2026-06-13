import logging
import logging.handlers
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from Backend.services.db_service import init_db
from Backend.routes import auth, chat, upload, status as status_route

# ── Logging setup ──────────────────────────────────────────────────────────────
def setup_logging() -> None:
    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / "app.log", maxBytes=5 * 1024 * 1024, backupCount=3
    )
    handlers.append(file_handler)
    logging.basicConfig(level=logging.INFO, format=fmt, handlers=handlers)


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="DRINKOO RAG Chatbot",
    description="Customer-facing chatbot website for DRINKOO beverages",
    version="1.0.0",
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(status_route.router, prefix="/api")

# Serve frontend static files — must be mounted LAST (catch-all)
_static_dir = Path("Frontend/static")
if _static_dir.exists():
    app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="static")


@app.on_event("startup")
def startup_event() -> None:
    setup_logging()
    os.makedirs("uploads", exist_ok=True)
    init_db()
    logging.getLogger(__name__).info("DRINKOO app started")
