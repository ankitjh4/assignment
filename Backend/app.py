"""FastAPI application factory for the DRINKOO RAG website."""
from __future__ import annotations

import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import PROJECT_ROOT, get_settings
from .database import init_db_if_needed
from .logging_config import configure_logging, get_logger, new_request_id
from .rag.indexer import build_index
from .routers import auth as auth_router
from .routers import catalog as catalog_router
from .routers import chat as chat_router
from .routers import pages as pages_router
from .routers import status as status_router
from .routers import text2sql as text2sql_router
from .routers import upload as upload_router

SETTINGS = get_settings()
LOG = get_logger("drinkoo.app")

FRONTEND_DIR = PROJECT_ROOT / "Frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    LOG.info("app_startup", extra={"env": SETTINGS.environment, "version": SETTINGS.app_version})
    init_db_if_needed()
    app.state.rag_index = build_index()
    LOG.info(
        "rag_index_ready",
        extra={"docs": len(app.state.rag_index.documents), "model": SETTINGS.openrouter_model},
    )
    yield
    LOG.info("app_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{SETTINGS.app_name} RAG Chatbot",
        version=SETTINGS.app_version,
        lifespan=lifespan,
    )

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.state.templates = templates

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or new_request_id()
        request.state.request_id = request_id
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            LOG.exception(
                "request_error",
                extra={"request_id": request_id, "path": request.url.path, "method": request.method},
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error.", "request_id": request_id},
            )
        latency_ms = int((time.perf_counter() - start) * 1000)
        response.headers["x-request-id"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if request.url.path.startswith("/static") or request.url.path.startswith("/api"):
            pass
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com data:; "
                "img-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'"
            )
        LOG.info(
            "http_request",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status": response.status_code,
                "latency_ms": latency_ms,
            },
        )
        return response

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        request_id = getattr(request.state, "request_id", None)
        if request.url.path.startswith("/api"):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "request_id": request_id},
            )
        if exc.status_code == 401:
            return _render_error(request, 401, "You must log in to view this page.", login_link=True)
        if exc.status_code == 404:
            return _render_error(request, 404, "Page not found.")
        return _render_error(request, exc.status_code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Invalid input.", "errors": exc.errors(), "request_id": request_id},
        )

    app.include_router(auth_router.router)
    app.include_router(chat_router.router)
    app.include_router(upload_router.router)
    app.include_router(status_router.router)
    app.include_router(catalog_router.router)
    app.include_router(text2sql_router.router)
    app.include_router(pages_router.router)

    return app


def _render_error(request: Request, code: int, message: str, login_link: bool = False) -> HTMLResponse:
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "code": code, "message": message, "login_link": login_link},
        status_code=code,
    )


app = create_app()
