"""Server-rendered HTML pages."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..config import get_settings
from ..deps import current_user_optional, require_user
from ..models import User

router = APIRouter(tags=["pages"])
SETTINGS = get_settings()


def _ctx(request: Request, user: Optional[User] = None, **extra) -> dict:
    return {
        "request": request,
        "user": user,
        "app_name": SETTINGS.app_name,
        "app_version": SETTINGS.app_version,
        "environment": SETTINGS.environment,
        "model_name": SETTINGS.openrouter_model,
        **extra,
    }


def _render(request: Request, name: str, **ctx) -> HTMLResponse:
    templates = request.app.state.templates
    return templates.TemplateResponse(name, _ctx(request, **ctx))


@router.get("/", response_class=HTMLResponse)
def home(request: Request, user: Optional[User] = Depends(current_user_optional)) -> HTMLResponse:
    return _render(request, "index.html", user=user, page="home")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user: Optional[User] = Depends(current_user_optional)) -> HTMLResponse:
    if user:
        return RedirectResponse(url="/chat", status_code=302)
    return _render(request, "login.html", user=None, page="login")


@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, user: Optional[User] = Depends(current_user_optional)) -> HTMLResponse:
    if user:
        return RedirectResponse(url="/chat", status_code=302)
    return _render(request, "signup.html", user=None, page="signup")


@router.get("/products", response_class=HTMLResponse)
def products_page(request: Request, user: Optional[User] = Depends(current_user_optional)) -> HTMLResponse:
    return _render(request, "products.html", user=user, page="products")


@router.get("/promotions", response_class=HTMLResponse)
def promotions_page(request: Request, user: Optional[User] = Depends(current_user_optional)) -> HTMLResponse:
    return _render(request, "promotions.html", user=user, page="promotions")


@router.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request, user: User = Depends(require_user)) -> HTMLResponse:
    return _render(request, "chat.html", user=user, page="chat")


@router.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request, user: User = Depends(require_user)) -> HTMLResponse:
    return _render(request, "upload.html", user=user, page="upload")


@router.get("/status", response_class=HTMLResponse)
def status_page(request: Request, user: Optional[User] = Depends(current_user_optional)) -> HTMLResponse:
    return _render(request, "status.html", user=user, page="status")
