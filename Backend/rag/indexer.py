"""Builds an in-memory hybrid (BM25 + TF-IDF-like) index over DRINKOO data.

The index aggregates content from:
- products  (name, description, flavor, category, sparkling, sugar, bulk)
- ingredients linked per product
- promotions (active and expired)
- support_articles
- static FAQ / policy documents

Each chunk carries metadata for source attribution so the generator can build
citations like [products:Citrus Zing] or [support:return-policy].
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text

from ..config import PROJECT_ROOT
from ..database import session_scope


_TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


def tokenize(text_value: str) -> List[str]:
    return [tok.lower() for tok in _TOKEN_RE.findall(text_value or "")]


@dataclass
class Document:
    doc_id: str
    source: str
    source_id: str
    title: str
    body: str
    tokens: List[str] = field(default_factory=list)


@dataclass
class HybridIndex:
    documents: List[Document]
    df: Dict[str, int]
    idf: Dict[str, float]
    doc_term_freq: List[Dict[str, int]]
    doc_len: List[int]
    avg_doc_len: float
    k1: float = 1.5
    b: float = 0.75

    def score(self, query_tokens: List[str]) -> List[Tuple[int, float]]:
        if not query_tokens or not self.documents:
            return []
        scores: List[Tuple[int, float]] = []
        for idx, tf_map in enumerate(self.doc_term_freq):
            bm25_score = 0.0
            tfidf_score = 0.0
            dl = self.doc_len[idx] or 1
            for term in query_tokens:
                tf = tf_map.get(term, 0)
                if tf == 0:
                    continue
                idf = self.idf.get(term, 0.0)
                # BM25 contribution
                denom = tf + self.k1 * (1 - self.b + self.b * dl / (self.avg_doc_len or 1))
                bm25_score += idf * ((tf * (self.k1 + 1)) / denom)
                # TF-IDF contribution
                tfidf_score += (tf / dl) * idf
            combined = 0.5 * bm25_score + 0.5 * tfidf_score
            if combined > 0:
                scores.append((idx, combined))
        scores.sort(key=lambda pair: pair[1], reverse=True)
        return scores


def _faq_documents() -> List[Document]:
    docs: List[Document] = []
    docs_dir = PROJECT_ROOT / "Backend" / "docs"
    for path in sorted(docs_dir.glob("*.md")) if docs_dir.exists() else []:
        body = path.read_text(encoding="utf-8")
        slug = path.stem
        title = slug.replace("-", " ").title()
        docs.append(
            Document(
                doc_id=f"docs:{slug}",
                source="docs",
                source_id=slug,
                title=title,
                body=body,
            )
        )
    return docs


def _load_documents() -> List[Document]:
    documents: List[Document] = []
    with session_scope() as session:
        product_rows = session.execute(
            text(
                """
                SELECT p.id, p.name, p.category, p.flavor, p.is_sparkling,
                       p.sugar_g_per_100ml, p.calories_per_100ml, p.price_cents,
                       p.supports_bulk, p.description
                FROM products p
                ORDER BY p.id
                """
            )
        ).mappings().all()

        ing_rows = session.execute(
            text(
                """
                SELECT p.id AS product_id, p.name AS product_name,
                       i.name AS ingredient_name, pi.percentage
                FROM product_ingredients pi
                JOIN products p ON p.id = pi.product_id
                JOIN ingredients i ON i.id = pi.ingredient_id
                ORDER BY p.id, i.name
                """
            )
        ).mappings().all()

        ingredients_by_product: Dict[int, List[str]] = {}
        for row in ing_rows:
            ingredients_by_product.setdefault(row["product_id"], []).append(
                f"{row['ingredient_name']} ({row['percentage']}%)"
            )

        for prod in product_rows:
            sparkling = "sparkling" if prod["is_sparkling"] else "still"
            bulk_text = "supports bulk orders" if prod["supports_bulk"] else "not bulk-eligible"
            sugar = prod["sugar_g_per_100ml"]
            sugar_tag = "zero sugar" if sugar == 0 else ("low sugar" if sugar < 4 else "regular sugar")
            ingredients = ", ".join(ingredients_by_product.get(prod["id"], [])) or "no listed ingredients"
            body = (
                f"{prod['name']} is a {sparkling} {prod['category']} drink with {prod['flavor'] or 'natural'} flavor and {sugar_tag}. "
                f"Sugar {sugar} g per 100ml. "
                f"Calories {prod['calories_per_100ml']} per 100ml. "
                f"Price {prod['price_cents']} cents. {bulk_text.capitalize()}. "
                f"DRINKOO product category: {prod['category']}. "
                f"Ingredients: {ingredients}. "
                f"Description: {prod['description'] or ''}"
            )
            documents.append(
                Document(
                    doc_id=f"products:{prod['id']}",
                    source="products",
                    source_id=prod["name"],
                    title=prod["name"],
                    body=body,
                )
            )

        promo_rows = session.execute(
            text(
                """
                SELECT id, code, title, description, applies_to_category,
                       discount_pct, starts_at, ends_at, is_active
                FROM promotions ORDER BY id
                """
            )
        ).mappings().all()
        for promo in promo_rows:
            active = "active" if promo["is_active"] else "expired"
            cat = promo["applies_to_category"] or "all categories"
            body = (
                f"{promo['title']} ({promo['code']}). {promo['description']} "
                f"Status: {active}. Applies to: {cat}. Discount: {promo['discount_pct']}%. "
                f"Valid {promo['starts_at']} to {promo['ends_at']}."
            )
            documents.append(
                Document(
                    doc_id=f"promotions:{promo['id']}",
                    source="promotions",
                    source_id=promo["code"],
                    title=promo["title"],
                    body=body,
                )
            )

        article_rows = session.execute(
            text("SELECT id, slug, title, body, tags FROM support_articles ORDER BY id")
        ).mappings().all()
        for article in article_rows:
            body = f"{article['title']}. {article['body']} Tags: {article['tags']}."
            documents.append(
                Document(
                    doc_id=f"support:{article['slug']}",
                    source="support",
                    source_id=article["slug"],
                    title=article["title"],
                    body=body,
                )
            )

    documents.extend(_faq_documents())
    return documents


def build_index() -> HybridIndex:
    documents = _load_documents()
    for doc in documents:
        doc.tokens = tokenize(f"{doc.title} {doc.body}")

    doc_term_freq: List[Dict[str, int]] = []
    df: Dict[str, int] = {}
    doc_len: List[int] = []
    for doc in documents:
        tf: Dict[str, int] = {}
        for token in doc.tokens:
            tf[token] = tf.get(token, 0) + 1
        doc_term_freq.append(tf)
        doc_len.append(len(doc.tokens))
        for term in tf.keys():
            df[term] = df.get(term, 0) + 1

    n = max(len(documents), 1)
    idf = {
        term: math.log(1 + (n - count + 0.5) / (count + 0.5))
        for term, count in df.items()
    }
    avg_doc_len = (sum(doc_len) / n) if doc_len else 0.0

    return HybridIndex(
        documents=documents,
        df=df,
        idf=idf,
        doc_term_freq=doc_term_freq,
        doc_len=doc_len,
        avg_doc_len=avg_doc_len,
    )
