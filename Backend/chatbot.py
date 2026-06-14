"""Protected chatbot endpoint — retrieves DRINKOO context then calls OpenRouter."""

import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import ChatSession, User
from rag import call_openrouter, retrieve_context

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chatbot"])


class ChatRequest(BaseModel):
    question: str
    image_description: str | None = None


class ChatResponse(BaseModel):
    answer: str
    retrieved_context: str
    session_id: int


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = body.question.strip()
    if not question:
        return ChatResponse(answer="Please enter a question.", retrieved_context="", session_id=0)

    # Prompt injection guard: reject adversarial instruction patterns
    injection_patterns = ["ignore previous", "ignore all", "disregard", "new instructions", "system prompt"]
    if any(p in question.lower() for p in injection_patterns):
        logger.warning("Prompt injection attempt by user %s: %s", current_user.email, question[:80])
        return ChatResponse(
            answer="I can only answer questions about DRINKOO products and services.",
            retrieved_context="",
            session_id=0,
        )

    logger.info("Chat request from %s: %s", current_user.email, question[:80])

    # RAG: retrieve grounded context from DRINKOO DB
    context = retrieve_context(question, db)
    logger.info("Retrieved context length: %d chars", len(context))

    # LLM: generate grounded answer via OpenRouter
    answer = await call_openrouter(question, context, body.image_description)

    # Persist chat session
    session = ChatSession(
        user_id=current_user.id,
        question=question,
        retrieved_context=context[:4000] if context else None,
        answer=answer,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return ChatResponse(
        answer=answer,
        retrieved_context=context,
        session_id=session.id,
    )
