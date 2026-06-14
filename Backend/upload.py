"""Protected image upload endpoint with file type, size, and path safety validation."""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from auth import get_current_user
from config import ALLOWED_IMAGE_EXTENSIONS, ALLOWED_IMAGE_TYPES, MAX_UPLOAD_SIZE_BYTES, UPLOAD_DIR
from models import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["upload"])


class UploadResponse(BaseModel):
    filename: str
    original_name: str
    content_type: str
    size_bytes: int
    message: str


def _safe_filename(original: str) -> str:
    """Generate a UUID-based filename with a safe extension — prevents path traversal."""
    ext = Path(original).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        ext = ".bin"
    return f"{uuid.uuid4().hex}{ext}"


@router.post("/upload", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    # Validate content_type header
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{file.content_type}' is not allowed. Accepted: {', '.join(sorted(ALLOWED_IMAGE_TYPES))}",
        )

    # Validate extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File extension '{ext}' is not allowed.",
        )

    # Read and enforce file size limit
    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {len(data):,} bytes exceeds the {MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB limit.",
        )

    # Save safely — never trust the original filename for the path
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = _safe_filename(file.filename or "upload")
    dest = UPLOAD_DIR / safe_name

    dest.write_bytes(data)
    logger.info("User %s uploaded %s (%d bytes) → %s", current_user.email, file.filename, len(data), safe_name)

    return UploadResponse(
        filename=safe_name,
        original_name=file.filename or "",
        content_type=file.content_type,
        size_bytes=len(data),
        message="Image uploaded successfully.",
    )
