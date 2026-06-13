from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    question: str
    image_filename: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    context_used: str
    session_id: int
    sql_query: Optional[str] = None
    sql_rows: Optional[list[dict]] = None
