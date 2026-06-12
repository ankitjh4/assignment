"""Answer generation: OpenRouter HTTP call with a deterministic offline fallback.

At runtime the chatbot uses OpenRouter (`nvidia/nemotron-3-ultra-550b-a55b:free`)
via the user's `OPENROUTER_API_KEY`. When the key is absent (e.g. CI, tests),
we fall back to an extractive, citation-preserving response built purely from
the retrieved snippets so the app is still grounded and deterministic.
"""
from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx

from ..config import get_settings
from ..logging_config import get_logger
from .grounding import REFUSAL_MESSAGE, UNKNOWN_MESSAGE
from .prompt import SYSTEM_PROMPT, render_user_prompt
from .retriever import RetrievedSnippet, citations, context_block

LOG = get_logger("drinkoo.rag.generator")
SETTINGS = get_settings()


@dataclass
class Generation:
    answer: str
    used_fallback: bool
    model: str
    raw_status: Optional[int] = None
    error: Optional[str] = None


def _openrouter_request(messages: List[Dict[str, str]]) -> Generation:
    headers = {
        "Authorization": f"Bearer {SETTINGS.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://drinkoo.local",
        "X-Title": "DRINKOO RAG Chatbot",
    }
    url = f"{SETTINGS.openrouter_base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": SETTINGS.openrouter_model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 400,
    }
    try:
        with httpx.Client(timeout=SETTINGS.openrouter_timeout_seconds) as client:
            response = client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            LOG.warning(
                "openrouter_error",
                extra={"status": response.status_code, "model": SETTINGS.openrouter_model},
            )
            return Generation("", True, SETTINGS.openrouter_model, response.status_code, response.text[:200])
        data = response.json()
        choices = data.get("choices") or []
        if not choices:
            return Generation("", True, SETTINGS.openrouter_model, response.status_code, "no_choices")
        content = (choices[0].get("message") or {}).get("content") or ""
        return Generation(content.strip(), False, SETTINGS.openrouter_model, response.status_code)
    except Exception as exc:
        LOG.warning("openrouter_exception", extra={"exc": str(exc)})
        return Generation("", True, SETTINGS.openrouter_model, None, str(exc))


def _extractive_fallback(user_question: str, snippets: List[RetrievedSnippet]) -> str:
    """Builds a grounded answer purely from retrieved snippets.

    Sentence selection: pick the highest-overlap sentences with the question
    tokens from each snippet, then stitch them with citations. This keeps the
    response grounded and deterministic for tests and CI.
    """
    if not snippets:
        return f"{UNKNOWN_MESSAGE} You could try asking about our products, ingredients, promotions, or support policies."

    question_tokens = {tok.lower() for tok in re.findall(r"[A-Za-z0-9]+", user_question or "")}
    pieces: List[str] = []
    used_citations: List[str] = []

    for snip in snippets[:3]:
        sentences = re.split(r"(?<=[.!?])\s+", snip.body)
        best_sentence: Optional[str] = None
        best_overlap = -1
        for sentence in sentences:
            tokens = {tok.lower() for tok in re.findall(r"[A-Za-z0-9]+", sentence)}
            overlap = len(tokens & question_tokens)
            if overlap > best_overlap and sentence.strip():
                best_overlap = overlap
                best_sentence = sentence.strip()
        sentence_to_use = best_sentence or sentences[0].strip() if sentences else snip.short_body(160)
        citation = snip.citation()
        used_citations.append(citation)
        pieces.append(f"{sentence_to_use} {citation}")

    body = " ".join(pieces)
    return textwrap.fill(body, width=4000)


def generate_answer(
    user_question: str,
    snippets: List[RetrievedSnippet],
    image_metadata: str = "",
    sql_table_refs: str = "",
    force_fallback: bool = False,
) -> Generation:
    if not snippets:
        return Generation(
            answer=f"{UNKNOWN_MESSAGE} Try asking about a specific DRINKOO product, promotion, or support policy.",
            used_fallback=True,
            model=SETTINGS.openrouter_model,
        )

    context = context_block(snippets)
    user_prompt = render_user_prompt(
        user_question=user_question,
        retrieved_context=context,
        sql_table_refs=sql_table_refs,
        image_metadata=image_metadata,
    )

    if not force_fallback and SETTINGS.has_openrouter_key:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        gen = _openrouter_request(messages)
        if gen.answer and not gen.used_fallback:
            return gen
        LOG.info("falling_back_to_local", extra={"reason": gen.error or "empty_response"})

    answer = _extractive_fallback(user_question, snippets)
    return Generation(answer=answer, used_fallback=True, model=SETTINGS.openrouter_model)


def refusal_response() -> Generation:
    return Generation(
        answer=REFUSAL_MESSAGE,
        used_fallback=True,
        model=SETTINGS.openrouter_model,
    )


def attach_citations(answer: str, snippets: List[RetrievedSnippet]) -> str:
    """Ensure at least one citation is present in the final answer."""
    if not snippets:
        return answer
    citation_tokens = citations(snippets)
    if any(token in answer for token in citation_tokens):
        return answer
    return f"{answer.rstrip()} {' '.join(citation_tokens[:2])}"
