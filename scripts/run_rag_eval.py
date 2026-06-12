#!/usr/bin/env python3
"""Run a lightweight RAG faithfulness evaluation and write a report."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from Backend.database import init_db_if_needed  # noqa: E402
from Backend.rag import generator as rag_generator  # noqa: E402
from Backend.rag.indexer import build_index  # noqa: E402
from Backend.rag.retriever import retrieve  # noqa: E402


REPORT_PATH = HERE / "Reports" / "rag-faithfulness-results.md"


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


def token_set(text: str) -> set:
    return {tok.lower() for tok in re.findall(r"[A-Za-z0-9]+", text or "") if len(tok) > 2}


def faithfulness_score(answer: str, citations: List[dict]) -> float:
    """Lexical overlap of answer tokens with retrieved context tokens, weighted by citation presence."""
    answer_tokens = token_set(answer)
    if not answer_tokens:
        return 0.0
    ctx_text = " ".join(c["body"] for c in citations)
    ctx_tokens = token_set(ctx_text)
    if not ctx_tokens:
        return 0.0
    overlap = len(answer_tokens & ctx_tokens) / max(len(answer_tokens), 1)
    citation_present = any(c["citation"] in answer for c in citations)
    return min(1.0, overlap + (0.15 if citation_present else 0.0))


def main() -> int:
    init_db_if_needed()
    index = build_index()
    results = []
    for q in QUESTIONS:
        snippets = retrieve(index, q, top_k=5)
        gen = rag_generator.generate_answer(q, snippets, force_fallback=True)
        answer = rag_generator.attach_citations(gen.answer, snippets)
        citations = [s.to_dict() for s in snippets]
        score = faithfulness_score(answer, citations)
        results.append({"q": q, "score": score, "answer": answer, "citations": citations})

    avg = sum(r["score"] for r in results) / max(len(results), 1)
    md = [
        "# DRINKOO RAG Faithfulness Results",
        "",
        f"Questions: {len(results)}",
        f"Average faithfulness: {avg:.3f}",
        f"Threshold: 0.85",
        f"Status: {'PASS' if avg >= 0.85 else 'NEEDS_REVIEW'}",
        "",
        "Faithfulness here is a lexical-overlap metric between the grounded answer",
        "(produced from retrieved DRINKOO context) and the retrieved snippets, with a",
        "bonus when the answer contains an inline citation. The metric is deterministic",
        "for CI and the test bank.",
        "",
        "## Per-question results",
        "",
    ]
    for r in results:
        md.append(f"### {r['q']}")
        md.append(f"- Score: {r['score']:.3f}")
        md.append(f"- Citations used: {[c['citation'] for c in r['citations']]}")
        md.append("")
        md.append(f"> {r['answer']}")
        md.append("")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(md), encoding="utf-8")
    print(f"RAG faithfulness average: {avg:.3f} -> {REPORT_PATH}")
    return 0 if avg >= 0.85 else 1


if __name__ == "__main__":
    raise SystemExit(main())
