import logging
import time
import httpx
from typing import Optional

from Backend import config
from Backend.services import db_service
from Backend.models.chat import ChatResponse

logger = logging.getLogger(__name__)

STOPWORDS = {"a", "an", "the", "is", "are", "was", "were", "what", "which", "how",
             "do", "does", "did", "for", "of", "in", "on", "at", "to", "and", "or",
             "can", "i", "me", "my", "we", "our", "you", "your", "it", "its", "with",
             "about", "there", "any", "some", "be", "have", "has", "if", "but",
             "should", "would", "could", "will", "get"}


def _tokenize(text: str) -> list[str]:
    words = text.lower().split()
    return [w.strip("?.,!") for w in words if w.strip("?.,!") not in STOPWORDS and len(w) > 2]


def retrieve_context(question: str) -> str:
    """Keyword search over products, support_articles, and promotions."""
    keywords = _tokenize(question)
    if not keywords:
        return ""

    scored: list[tuple[int, str]] = []

    # Search products
    for kw in keywords:
        pattern = f"%{kw}%"
        rows = db_service.execute_query(
            "SELECT name, category, description, price, sugar_grams, is_bulk_available "
            "FROM products WHERE is_available = 1 AND ("
            "LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(category) LIKE ?)",
            (pattern, pattern, pattern),
        )
        for row in rows:
            entry = (
                f"[Product] {row['name']} (category: {row['category']}, "
                f"price: £{row['price']:.2f}, sugar: {row['sugar_grams']}g, "
                f"bulk: {'yes' if row['is_bulk_available'] else 'no'}): {row['description']}"
            )
            scored.append((1, entry))

    # Search support articles
    for kw in keywords:
        pattern = f"%{kw}%"
        rows = db_service.execute_query(
            "SELECT title, content, category FROM support_articles "
            "WHERE LOWER(title) LIKE ? OR LOWER(content) LIKE ?",
            (pattern, pattern),
        )
        for row in rows:
            entry = f"[Support] {row['title']}: {row['content'][:600]}"
            scored.append((1, entry))

    # Search active promotions
    for kw in keywords:
        pattern = f"%{kw}%"
        rows = db_service.execute_query(
            "SELECT title, description, discount_percent, end_date FROM promotions "
            "WHERE is_active = 1 AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)",
            (pattern, pattern),
        )
        for row in rows:
            entry = (
                f"[Promotion] {row['title']}: {row['description']} "
                f"({row['discount_percent']}% off, valid until {row['end_date']})"
            )
            scored.append((1, entry))

    # Also fetch all active promotions when question mentions promotions/discount/offer
    promo_triggers = {"promotion", "promotions", "discount", "offer", "sale", "deal", "code"}
    if any(kw in promo_triggers for kw in keywords):
        rows = db_service.execute_query(
            "SELECT title, description, discount_percent, end_date FROM promotions WHERE is_active = 1"
        )
        for row in rows:
            entry = (
                f"[Promotion] {row['title']}: {row['description']} "
                f"({row['discount_percent']}% off, valid until {row['end_date']})"
            )
            scored.append((2, entry))

    # Deduplicate and take top results
    seen: set[str] = set()
    unique: list[str] = []
    for _, entry in sorted(scored, key=lambda x: -x[0]):
        if entry not in seen:
            seen.add(entry)
            unique.append(entry)
        if len(unique) >= 8:
            break

    context = "\n".join(unique)
    logger.info("RAG retrieval: %d context items for question '%s...'", len(unique), question[:50])
    return context


def _openrouter_call(payload: dict, label: str) -> dict | None:
    """POST to OpenRouter with one retry on 429. Returns parsed JSON or None."""
    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://drinkoo.app",
        "X-Title": f"DRINKOO {label}",
    }
    for attempt in range(3):
        try:
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0,
            )
            if response.status_code == 429:
                wait = min(int(response.headers.get("retry-after", 5)) + attempt * 5, 20)
                logger.warning("%s: 429 rate-limited, retrying in %ds (attempt %d)", label, wait, attempt + 1)
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error("%s: request timed out", label)
            return None
        except Exception as exc:
            logger.error("%s error: %s", label, exc)
            return None
    logger.error("%s: still rate-limited after 3 retries", label)
    return None


_SCHEMA_SUMMARY = """
Tables in the DRINKOO SQLite database:
- products(id, name, category, description, price, is_available, sugar_grams, is_bulk_available, created_at)
- ingredients(id, name, description, allergen_info)
- product_ingredients(product_id, ingredient_id, quantity)
- orders(id, user_id, product_id, quantity, status, created_at)
- support_articles(id, title, content, category, created_at)
- promotions(id, title, description, discount_percent, start_date, end_date, is_active)
- chat_sessions(id, user_id, question, context_used, answer, created_at)
- users(id, username, email, password_hash, created_at)
"""


def _is_safe_sql(sql: str) -> bool:
    """Allow only SELECT statements; reject anything that mutates data."""
    normalized = sql.strip().upper()
    if not normalized.startswith("SELECT"):
        return False
    for dangerous in ("DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE",
                      "ATTACH", "DETACH", "PRAGMA", "VACUUM"):
        if dangerous in normalized:
            return False
    return True


def generate_sql(question: str) -> tuple[str, list[dict]]:
    """Ask the LLM to translate the question to SQL, execute it, return (sql, rows)."""
    if not config.OPENROUTER_API_KEY:
        return "", []

    system_prompt = (
        "You are a SQL expert for a SQLite database. "
        "Given the schema and a natural-language question, write a single valid SQLite SELECT query. "
        "Return ONLY the raw SQL query — no explanation, no markdown, no code fences. "
        "The query must start with SELECT. "
        "Never use DROP, DELETE, UPDATE, INSERT, ALTER, or PRAGMA."
    )
    user_prompt = f"Schema:\n{_SCHEMA_SUMMARY}\n\nQuestion: {question}\n\nSQL:"

    data = _openrouter_call(
        {
            "model": config.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
            "max_tokens": 256,
        },
        label="Text2SQL",
    )
    if not data:
        return "", []

    raw_sql = data["choices"][0]["message"]["content"].strip()

    # Strip markdown fences if the model wrapped the SQL anyway
    if raw_sql.startswith("```"):
        raw_sql = "\n".join(
            line for line in raw_sql.splitlines()
            if not line.startswith("```")
        ).strip()

    if not _is_safe_sql(raw_sql):
        logger.warning("Text2SQL produced unsafe SQL, skipping: %s", raw_sql[:120])
        return raw_sql, []

    try:
        rows = db_service.execute_query(raw_sql)
    except Exception as exc:
        logger.error("Text2SQL query execution failed: %s", exc)
        return raw_sql, []

    logger.info("Text2SQL: '%s...' → %d rows", raw_sql[:60], len(rows))
    return raw_sql, rows


def generate_answer(question: str, context: str) -> str:
    """Call OpenRouter to generate a grounded answer."""
    if not config.OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY is not set")
        return "The chatbot is not configured. Please contact support."

    if not context:
        context = "No relevant DRINKOO data was found for this question."

    system_prompt = (
        "You are the DRINKOO customer assistant. "
        "Answer questions using ONLY the retrieved context provided below. "
        "If the answer is not found in the retrieved context, say "
        "\"I don't have that information in the DRINKOO data.\" "
        "Never invent product names, prices, ingredients, or policies. "
        "When you use retrieved context, mention which product or article you are referencing. "
        "Keep answers concise and helpful. "
        "Do not answer questions unrelated to DRINKOO products, orders, or policies."
    )

    user_prompt = f"Retrieved context:\n{context}\n\nUser question:\n{question}"

    data = _openrouter_call(
        {
            "model": config.OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 512,
        },
        label="Chatbot",
    )
    if not data:
        return "The chatbot is temporarily unavailable. Please try again in a moment."
    return data["choices"][0]["message"]["content"].strip()


def chat(question: str, user_id: int, image_filename: Optional[str] = None) -> ChatResponse:
    """Orchestrate Text2SQL + keyword retrieval → generation → session logging."""
    sql_query, sql_rows = generate_sql(question)
    context = retrieve_context(question)

    # Augment context with SQL result rows so the LLM can reference them
    if sql_rows:
        sql_context = "[SQL Results]\n" + "\n".join(
            ", ".join(f"{k}: {v}" for k, v in row.items()) for row in sql_rows[:10]
        )
        context = sql_context + ("\n\n" + context if context else "")

    answer = generate_answer(question, context)

    session_id = db_service.execute_write(
        "INSERT INTO chat_sessions (user_id, question, context_used, answer) VALUES (?,?,?,?)",
        (user_id, question, context[:2000], answer),
    )
    return ChatResponse(
        answer=answer,
        context_used=context,
        session_id=session_id,
        sql_query=sql_query or None,
        sql_rows=sql_rows if sql_rows else None,
    )
