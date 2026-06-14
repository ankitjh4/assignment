"""
File upload routes for DRINKOO API.
Handles image uploads with validation.
"""
import logging
import os
import secrets
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from pydantic import BaseModel
from backend.config import Config
from backend.auth import TokenData
from backend.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])


class UploadResponse(BaseModel):
    status: str
    filename: str
    file_path: str
    size_bytes: int


@router.post("/image", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """Upload and validate image file."""
    try:
        # Validate MIME type
        if file.content_type not in Config.ALLOWED_MIME_TYPES:
            logger.warning(
                f"Upload rejected for {current_user.username}: "
                f"invalid MIME type {file.content_type}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {', '.join(Config.ALLOWED_MIME_TYPES)}"
            )
        
        # Read file content and check size
        content = await file.read()
        
        if len(content) > Config.MAX_UPLOAD_SIZE_BYTES:
            logger.warning(
                f"Upload rejected for {current_user.username}: "
                f"file too large ({len(content)} bytes)"
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Max size: {Config.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Generate safe filename
        file_extension = Path(file.filename).suffix
        safe_filename = f"{current_user.user_id}_{secrets.token_hex(8)}{file_extension}"
        
        # Create upload directory if needed
        upload_path = Path(Config.UPLOAD_DIR)
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_path / safe_filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(
            f"File uploaded by {current_user.username}: "
            f"{safe_filename} ({len(content)} bytes)"
        )
        
        return UploadResponse(
            status="success",
            filename=safe_filename,
            file_path=str(file_path),
            size_bytes=len(content)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error for {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed"
        )


@router.get("/image/{filename}")
async def get_image(filename: str, current_user: TokenData = Depends(get_current_user)):
    """Download uploaded image (with ownership validation)."""
    try:
        # Security: only allow user to access their own files
        if not filename.startswith(f"{current_user.user_id}_"):
            logger.warning(
                f"Unauthorized file access attempt by {current_user.username}: {filename}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unauthorized"
            )
        
        file_path = Path(Config.UPLOAD_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        logger.info(f"File accessed by {current_user.username}: {filename}")
        
        return {"file_path": str(file_path)}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File access error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File retrieval failed"
        )
