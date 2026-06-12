"""Protected chat endpoint that runs the RAG pipeline and returns a grounded answer."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..deps import get_db, require_user
from ..logging_config import get_logger
from ..models import ChatSession, User
from ..rag import generator as rag_generator
from ..rag.grounding import detect_injection
from ..rag.retriever import retrieve, citations as build_citations

router = APIRouter(prefix="/api/chat", tags=["chat"])
LOG = get_logger("drinkoo.chat")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: Optional[int] = None
    force_offline: bool = False


class Citation(BaseModel):
    source: str
    source_id: str
    title: str
    body: str
    score: float
    citation: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    refused: bool
    refusal_reason: Optional[str] = None
    model: str
    used_fallback: bool
    retrieved_doc_ids: List[str]
    session_id: int


def _ensure_session(db: Session, user_id: int, session_id: Optional[int]) -> ChatSession:
    if session_id:
        existing = db.get(ChatSession, session_id)
        if existing and existing.user_id == user_id:
            return existing
    session = ChatSession(user_id=user_id, message_count=0)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    request: Request,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    index = getattr(request.app.state, "rag_index", None)
    if index is None:
        raise HTTPException(status_code=503, detail="RAG index is not ready yet.")

    decision = detect_injection(payload.message)
    chat_session = _ensure_session(db, user.id, payload.session_id)

    if decision.refuse:
        gen = rag_generator.refusal_response()
        LOG.info(
            "chat_refused",
            extra={
                "user_id": user.id,
                "session_id": chat_session.id,
                "reason": decision.reason,
            },
        )
        chat_session.message_count += 1
        db.execute(
            text("UPDATE chat_sessions SET last_message_at = datetime('now'), message_count = :c WHERE id = :id"),
            {"c": chat_session.message_count, "id": chat_session.id},
        )
        db.commit()
        return ChatResponse(
            answer=gen.answer,
            citations=[],
            refused=True,
            refusal_reason=decision.reason,
            model=gen.model,
            used_fallback=gen.used_fallback,
            retrieved_doc_ids=[],
            session_id=chat_session.id,
        )

    snippets = retrieve(index, payload.message, top_k=5)
    gen = rag_generator.generate_answer(
        payload.message,
        snippets,
        force_fallback=payload.force_offline,
    )
    answer = rag_generator.attach_citations(gen.answer, snippets)

    LOG.info(
        "chat_event",
        extra={
            "user_id": user.id,
            "session_id": chat_session.id,
            "model": gen.model,
            "used_fallback": gen.used_fallback,
            "retrieved": [s.citation() for s in snippets],
            "refused": False,
        },
    )

    chat_session.message_count += 1
    db.execute(
        text("UPDATE chat_sessions SET last_message_at = datetime('now'), message_count = :c WHERE id = :id"),
        {"c": chat_session.message_count, "id": chat_session.id},
    )
    db.commit()

    return ChatResponse(
        answer=answer,
        citations=[Citation(**snip.to_dict()) for snip in snippets],
        refused=False,
        model=gen.model,
        used_fallback=gen.used_fallback,
        retrieved_doc_ids=[snip.citation() for snip in snippets],
        session_id=chat_session.id,
    )
