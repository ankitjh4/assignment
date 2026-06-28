"""
Chatbot routes for DRINKOO API.
Handles RAG-powered chatbot interactions.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from backend.auth import verify_token, TokenData, get_user_by_id
from backend.rag_service import process_chatbot_query
from backend.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    status: str
    query: str
    response: str
    context: dict


@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(request: ChatRequest, current_user: TokenData = Depends(get_current_user)):
    """Process user question through RAG chatbot."""
    try:
        # Validate input
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        if len(request.message) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message too long (max 1000 characters)"
            )
        
        # Process through RAG pipeline
        result = process_chatbot_query(request.message)
        
        if result["status"] == "error":
            logger.warning(f"Chatbot error for user {current_user.username}: {result['response']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["response"]
            )
        
        logger.info(
            f"Chatbot query processed for {current_user.username}: "
            f"{len(result['context'])} context items"
        )
        
        return ChatResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chatbot processing failed"
        )


@router.get("/history")
async def get_chat_history(current_user: TokenData = Depends(get_current_user)):
    """Get chat history for current user (stub for future implementation)."""
    return {
        "user_id": current_user.user_id,
        "history": []  # Would be retrieved from database in full implementation
    }
