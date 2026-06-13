import logging
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from Backend import config
from Backend.services.auth_service import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["upload"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Allowed: jpeg, png, gif, webp.",
        )

    contents = await file.read()

    if len(contents) > config.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed file size is {config.MAX_UPLOAD_BYTES // (1024*1024)} MB.",
        )

    ext = Path(file.filename).suffix.lower() if file.filename else ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        ext = ".jpg"

    safe_filename = uuid.uuid4().hex + ext
    upload_path = Path(config.UPLOAD_DIR) / safe_filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(contents)

    logger.info(
        "Image uploaded by user_id=%s: %s (%d bytes, %s)",
        current_user.get("user_id"),
        safe_filename,
        len(contents),
        file.content_type,
    )
    return {
        "filename": safe_filename,
        "original_name": file.filename,
        "size": len(contents),
        "content_type": file.content_type,
    }
