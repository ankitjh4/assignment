"""RAG faithfulness regression. Must hit >= 0.85 average."""
from __future__ import annotations

import re
from typing import List

from Backend.rag import generator as rag_generator
from Backend.rag.indexer import build_index
from Backend.rag.retriever import retrieve


QUESTIONS = [
    "Which DRINKOO products are low sugar?",
    "What ingredients are in Citrus Zing?",
    "Are there active promotions for sparkling beverages?",
    "What should a customer do if an order arrives damaged?",
    "Which products are available for bulk orders?",
    "Is there a tea promotion?",
    "What is the refund timeline?",
    "Which products contain Ginger Extract?",
    "Tell me about the kids drinks.",
    "What ingredients are flagged as allergens?",
]


def _tokens(text: str) -> set:
    return {tok.lower() for tok in re.findall(r"[A-Za-z0-9]+", text or "") if len(tok) > 2}


def _faithfulness(answer: str, citations: List[dict]) -> float:
    answer_tokens = _tokens(answer)
    if not answer_tokens:
        return 0.0
    ctx_tokens = _tokens(" ".join(c["body"] for c in citations))
    if not ctx_tokens:
        return 0.0
    overlap = len(answer_tokens & ctx_tokens) / max(len(answer_tokens), 1)
    citation_present = any(c["citation"] in answer for c in citations)
    return min(1.0, overlap + (0.15 if citation_present else 0.0))


def test_rag_faithfulness_average_threshold(client):
    index = build_index()
    scores = []
    for question in QUESTIONS:
        snippets = retrieve(index, question, top_k=5)
        gen = rag_generator.generate_answer(question, snippets, force_fallback=True)
        answer = rag_generator.attach_citations(gen.answer, snippets)
        citations = [s.to_dict() for s in snippets]
        scores.append(_faithfulness(answer, citations))
    average = sum(scores) / len(scores)
    assert average >= 0.85, f"RAG faithfulness {average:.3f} below 0.85 (per-question: {scores})"
