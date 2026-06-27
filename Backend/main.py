"""DRINKOO FastAPI application entry point."""

import logging
import logging.config
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import auth
import chatbot
import status
import upload
from database import init_db

# --- Logging setup ---
logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        }
    },
    "root": {"handlers": ["console"], "level": "INFO"},
})

logger = logging.getLogger(__name__)

# --- Lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("DRINKOO API started — DB initialised.")
    yield


# --- App ---
app = FastAPI(lifespan=lifespan,
    title="DRINKOO API",
    description="RAG chatbot backend for the DRINKOO beverage company.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Templates & static files ---
_frontend = Path(__file__).parent.parent / "Frontend"
templates = Jinja2Templates(directory=str(_frontend / "templates"))
app.mount("/static", StaticFiles(directory=str(_frontend / "static")), name="static")

# --- Routers ---
app.include_router(auth.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(status.router, prefix="/api")


# --- Global error handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# --- HTML page routes (Alpine.js + Jinja2 — no build step) ---
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse, include_in_schema=False)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse, include_in_schema=False)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse, include_in_schema=False)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/status", response_class=HTMLResponse, include_in_schema=False)
async def status_page(request: Request):
    return templates.TemplateResponse("status.html", {"request": request})
