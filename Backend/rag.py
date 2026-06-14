"""RAG retrieval layer — queries DRINKOO DB to build grounded context for the LLM."""

import asyncio
import logging
import re
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

logger = logging.getLogger(__name__)

# Keyword sets for routing queries to the right tables (include common plurals/variants)
_PRODUCT_KEYWORDS = {"product", "products", "drink", "drinks", "beverage", "beverages", "juice", "juices",
                     "water", "energy", "sparkling", "calories", "calorie", "sugar", "low sugar",
                     "bulk", "available", "category", "price"}
_INGREDIENT_KEYWORDS = {"ingredient", "ingredients", "contain", "contains", "made of", "made from",
                        "citrus", "vitamin", "vitamins", "caffeine", "allergen", "allergens",
                        "natural", "extract", "extracts", "composition"}
_PROMOTION_KEYWORDS = {"promotion", "promotions", "discount", "discounts", "deal", "deals",
                       "sale", "sales", "offer", "offers", "promo", "promos", "save", "saving", "savings"}
_SUPPORT_KEYWORDS = {"return", "returns", "refund", "refunds", "cancel", "cancellation", "cancellations",
                     "damage", "damaged", "delivery", "deliveries", "ship", "shipping", "contact",
                     "support", "policy", "policies", "how", "what should", "subscription", "subscriptions",
                     "loyalty"}
_ORDER_KEYWORDS = {"order", "orders", "status", "bulk order", "purchase", "purchases"}


def _keywords(question: str) -> set[str]:
    return set(re.findall(r"\b\w+\b", question.lower()))


def retrieve_context(question: str, db: Session) -> str:
    """Return a text block with DRINKOO data relevant to the question."""
    words = _keywords(question)
    sections: list[str] = []

    if words & _PRODUCT_KEYWORDS:
        rows = db.execute(
            text("""
                SELECT name, category, description, price, is_bulk_available, is_low_sugar, calories, stock_quantity
                FROM products
                ORDER BY name
            """)
        ).fetchall()
        if rows:
            lines = [
                f"- {r.name} ({r.category}): ${r.price:.2f}, "
                f"{'low-sugar' if r.is_low_sugar else 'regular'}, "
                f"{r.calories or 'N/A'} kcal, "
                f"bulk={'yes' if r.is_bulk_available else 'no'}, "
                f"stock={r.stock_quantity}"
                for r in rows
            ]
            sections.append("DRINKOO Products:\n" + "\n".join(lines))

    if words & _INGREDIENT_KEYWORDS:
        rows = db.execute(
            text("""
                SELECT p.name AS product, i.name AS ingredient, pi.quantity_mg
                FROM product_ingredients pi
                JOIN products p ON p.id = pi.product_id
                JOIN ingredients i ON i.id = pi.ingredient_id
                ORDER BY p.name, i.name
            """)
        ).fetchall()
        if rows:
            lines = [
                f"- {r.product}: {r.ingredient} ({r.quantity_mg or '?'} mg)"
                for r in rows
            ]
            sections.append("Product Ingredients:\n" + "\n".join(lines))

    if words & _PROMOTION_KEYWORDS:
        rows = db.execute(
            text("""
                SELECT pr.title, pr.discount_pct, pr.description, pr.expires_at, p.name AS product_name
                FROM promotions pr
                LEFT JOIN products p ON pr.product_id = p.id
                WHERE pr.active = 1
                ORDER BY pr.discount_pct DESC
            """)
        ).fetchall()
        if rows:
            lines = [
                f"- {r.title}: {r.discount_pct}% off "
                f"({'all sparkling' if r.product_name is None else r.product_name}), "
                f"expires {r.expires_at or 'N/A'}. {r.description or ''}"
                for r in rows
            ]
            sections.append("Active Promotions:\n" + "\n".join(lines))

    if words & _SUPPORT_KEYWORDS:
        rows = db.execute(
            text("""
                SELECT title, content
                FROM support_articles
                ORDER BY id
            """)
        ).fetchall()
        if rows:
            lines = [f"[{r.title}]: {r.content}" for r in rows]
            sections.append("Support Knowledge Base:\n" + "\n".join(lines))

    if words & _ORDER_KEYWORDS and not (words & _SUPPORT_KEYWORDS):
        rows = db.execute(
            text("""
                SELECT p.name AS product, o.quantity, o.total_price, o.status
                FROM orders o
                JOIN products p ON p.id = o.product_id
                ORDER BY o.created_at DESC
                LIMIT 5
            """)
        ).fetchall()
        if rows:
            lines = [
                f"- {r.product}: qty={r.quantity}, total=${r.total_price:.2f}, status={r.status}"
                for r in rows
            ]
            sections.append("Recent Orders:\n" + "\n".join(lines))

    if not sections:
        # Fallback: return product list and top support articles
        rows = db.execute(text("SELECT name, category FROM products ORDER BY name")).fetchall()
        if rows:
            sections.append("DRINKOO Products: " + ", ".join(f"{r.name} ({r.category})" for r in rows))

    return "\n\n".join(sections) if sections else ""


SYSTEM_PROMPT = """You are DRINKOO Assistant, a helpful chatbot for the DRINKOO beverage company.

Answer ONLY using the retrieved DRINKOO context provided below. Follow these rules:

1. If the answer is in the context, give a clear, concise answer and mention which product, table, or article your answer comes from.
2. If the answer is NOT in the context, say: "I don't have that information in the DRINKOO database. Please contact support@drinkoo.com for help."
3. Never invent product names, prices, ingredients, promotions, or policies that are not in the context.
4. Keep answers short and useful — 1 to 4 sentences.
5. If the user uploads an image, acknowledge it but do not make unsupported claims about the image content.
6. Do not answer questions unrelated to DRINKOO products, orders, ingredients, promotions, or support policies."""


async def call_openrouter(question: str, context: str, image_description: str | None = None) -> str:
    """Send question + retrieved context to OpenRouter and return the answer."""
    if not OPENROUTER_API_KEY:
        return (
            "OpenRouter API key is not configured. "
            "Set OPENROUTER_API_KEY in your environment to enable the chatbot."
        )

    user_content = f"""Retrieved DRINKOO context:
{context if context else 'No specific context found for this question.'}

User question: {question}"""

    if image_description:
        user_content += f"\n\nImage details provided by user: {image_description}"

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 512,
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://drinkoo.app",
        "X-Title": "DRINKOO RAG Chatbot",
    }

    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{OPENROUTER_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if response.status_code == 429:
                    # Respect the Retry-After hint from the provider
                    try:
                        retry_after = int(response.json()["error"]["metadata"].get("retry_after_seconds", 10))
                    except Exception:
                        retry_after = 10
                    logger.warning("OpenRouter rate limited — retrying in %ds (attempt %d/3)", retry_after, attempt + 1)
                    await asyncio.sleep(retry_after)
                    continue
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as exc:
            logger.error("OpenRouter HTTP error: %s — %s", exc.response.status_code, exc.response.text)
            if attempt == 2:
                return "The AI service returned an error. Please try again later."
        except Exception as exc:
            logger.error("OpenRouter call failed: %s", exc)
            if attempt == 2:
                return "The AI service is temporarily unavailable. Please try again later."

    return "The AI service is temporarily unavailable after retries. Please try again in a moment."
