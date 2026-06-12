"""Hybrid retriever over the DRINKOO index plus a small structured-row helper."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .indexer import HybridIndex, tokenize


@dataclass
class RetrievedSnippet:
    source: str
    source_id: str
    title: str
    body: str
    score: float

    def short_body(self, limit: int = 320) -> str:
        body = self.body.strip()
        if len(body) <= limit:
            return body
        return body[:limit].rstrip() + "..."

    def citation(self) -> str:
        return f"[{self.source}:{self.source_id}]"

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "source_id": self.source_id,
            "title": self.title,
            "body": self.short_body(),
            "score": round(float(self.score), 4),
            "citation": self.citation(),
        }


def retrieve(index: HybridIndex, query: str, top_k: int = 5, min_score: float = 0.05) -> List[RetrievedSnippet]:
    if not query.strip():
        return []
    tokens = tokenize(query)
    ranked = index.score(tokens)
    snippets: List[RetrievedSnippet] = []
    for idx, score in ranked[: max(top_k, 1)]:
        if score < min_score:
            continue
        doc = index.documents[idx]
        snippets.append(
            RetrievedSnippet(
                source=doc.source,
                source_id=doc.source_id,
                title=doc.title,
                body=doc.body,
                score=score,
            )
        )
    return snippets


def context_block(snippets: List[RetrievedSnippet]) -> str:
    lines: List[str] = []
    for idx, snip in enumerate(snippets, start=1):
        lines.append(
            f"[{idx}] source={snip.source} id={snip.source_id} title={snip.title!r} (score={snip.score:.3f})\n{snip.short_body()}"
        )
    return "\n\n".join(lines)


def citations(snippets: List[RetrievedSnippet]) -> List[str]:
    seen: List[str] = []
    for snip in snippets:
        token = snip.citation()
        if token not in seen:
            seen.append(token)
    return seen
