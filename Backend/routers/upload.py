"""Protected image upload endpoint with strict validation."""
from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..config import get_settings
from ..deps import require_user
from ..logging_config import get_logger
from ..models import User

router = APIRouter(prefix="/api/upload", tags=["upload"])
LOG = get_logger("drinkoo.upload")
SETTINGS = get_settings()

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
MAGIC_BYTES = {
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
    b"RIFF": "image/webp",
}
MAX_FILENAME_LENGTH = 80


class UploadResponse(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    url: str


def _sniff_mime(head: bytes) -> Optional[str]:
    for magic, mime in MAGIC_BYTES.items():
        if head.startswith(magic):
            return mime
    return None


def _safe_filename(original: str) -> str:
    name = Path(original).name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)[:MAX_FILENAME_LENGTH] or "upload"
    return name


def _resolve_upload_dir() -> Path:
    upload_dir = SETTINGS.upload_dir_path
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...), user: User = Depends(require_user)) -> UploadResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PNG, JPEG, and WebP images are accepted.",
        )

    original_ext = Path(file.filename or "").suffix.lower()
    if original_ext and original_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file extension.",
        )

    max_bytes = SETTINGS.max_upload_mb * 1024 * 1024
    head = await file.read(8)
    sniffed = _sniff_mime(head)
    if sniffed is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File content does not match a supported image format.",
        )

    contents = head + await file.read(max_bytes + 1)
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {SETTINGS.max_upload_mb} MB limit.",
        )

    upload_dir = _resolve_upload_dir()
    safe_name = _safe_filename(file.filename or "upload")
    extension = Path(safe_name).suffix or {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/webp": ".webp",
    }.get(sniffed, ".bin")
    new_name = f"{user.id}_{uuid.uuid4().hex}{extension}"
    target_path = (upload_dir / new_name).resolve()

    if not str(target_path).startswith(str(upload_dir.resolve())):
        raise HTTPException(status_code=400, detail="Invalid upload path.")

    target_path.write_bytes(contents)

    LOG.info(
        "upload_event",
        extra={
            "user_id": user.id,
            "stored_as": new_name,
            "content_type": sniffed,
            "bytes": len(contents),
        },
    )

    return UploadResponse(
        filename=new_name,
        content_type=sniffed,
        size_bytes=len(contents),
        url=f"/api/upload/files/{new_name}",
    )


@router.get("/files/{filename}")
def download_image(filename: str, user: User = Depends(require_user)) -> FileResponse:
    safe = _safe_filename(filename)
    upload_dir = _resolve_upload_dir().resolve()
    target = (upload_dir / safe).resolve()
    if not str(target).startswith(str(upload_dir)):
        raise HTTPException(status_code=400, detail="Invalid path.")
    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    if not safe.startswith(f"{user.id}_") and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed.")
    return FileResponse(target)
