import logging
from fastapi import APIRouter, Depends, HTTPException

from Backend.models.chat import ChatRequest, ChatResponse
from Backend.services.auth_service import get_current_user
from Backend.services import rag_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, current_user: dict = Depends(get_current_user)):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    user_id = current_user.get("user_id")
    logger.info("Chat request from user_id=%s question='%s...'", user_id, payload.question[:60])

    return rag_service.chat(
        question=payload.question,
        user_id=user_id,
        image_filename=payload.image_filename,
    )
