from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
import secrets
import sqlite3
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import requests
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field


ROOT_DIR = Path(__file__).resolve().parents[1]
DB_PATH = ROOT_DIR / "Database" / "drinkoo.db"
SCHEMA_PATH = ROOT_DIR / "Database" / "schema.sql"
SEED_PATH = ROOT_DIR / "Database" / "seed.sql"
UPLOAD_DIR = ROOT_DIR / "uploads"
FRONTEND_DIR = ROOT_DIR / "Frontend"
MAX_UPLOAD_SIZE = 2 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("drinkoo")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    with get_connection() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executescript(SEED_PATH.read_text(encoding="utf-8"))
        conn.commit()


def ensure_demo_user() -> None:
    demo_email = "demo@drinkoo.com"
    demo_password = "StrongPass123"
    demo_name = "Demo User"

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (demo_email,),
        ).fetchone()
        if existing:
            return

        conn.execute(
            "INSERT INTO users (email, full_name, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (demo_email, demo_name, hash_password(demo_password), int(time.time())),
        )
        conn.commit()
    logger.info("default demo user created email=%s", demo_email)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"{salt.hex()}:{digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt_hex, digest_hex = password_hash.split(":", maxsplit=1)
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(actual, expected)


def create_token() -> str:
    return secrets.token_urlsafe(32)


def create_session(user_id: int) -> str:
    token = create_token()
    now = int(time.time())
    expires_at = now + 7 * 24 * 60 * 60
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO auth_sessions (token, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, user_id, now, expires_at),
        )
        conn.commit()
    return token


def get_session_user_id(token: str) -> int | None:
    now = int(time.time())
    with get_connection() as conn:
        row = conn.execute(
            "SELECT user_id FROM auth_sessions WHERE token = ? AND expires_at > ?",
            (token, now),
        ).fetchone()
    if row is None:
        return None
    return int(row["user_id"])


def delete_session(token: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM auth_sessions WHERE token = ?", (token,))
        conn.commit()


def cleanup_expired_sessions() -> None:
    now = int(time.time())
    with get_connection() as conn:
        conn.execute("DELETE FROM auth_sessions WHERE expires_at <= ?", (now,))
        conn.commit()


STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "for",
    "and",
    "with",
    "what",
    "which",
    "tell",
    "about",
    "there",
    "any",
    "give",
    "me",
    "all",
    "under",
    "into",
    "from",
}

SYNONYM_MAP = {
    "beverages": ["drinks", "products"],
    "drink": ["products"],
    "drinks": ["products"],
    "promo": ["promotion", "promotions"],
    "sparkling": ["soda"],
    "support": ["policy", "article"],
}


def extract_terms(question: str) -> list[str]:
    raw = re.findall(r"[a-z0-9]+", question.lower())
    terms: list[str] = []
    for token in raw:
        if token in STOPWORDS or len(token) < 3:
            continue
        terms.append(token)
        terms.extend(SYNONYM_MAP.get(token, []))

    deduped: list[str] = []
    seen: set[str] = set()
    for term in terms:
        if term not in seen:
            seen.add(term)
            deduped.append(term)
    return deduped[:10]


def build_like_conditions(columns: list[str], terms: list[str]) -> tuple[str, list[str]]:
    if not terms:
        return "", []

    clauses: list[str] = []
    params: list[str] = []
    for term in terms:
        part = " OR ".join([f"lower({column}) LIKE ?" for column in columns])
        clauses.append(f"({part})")
        params.extend([f"%{term}%"] * len(columns))
    return " OR ".join(clauses), params


class SQLPlan(BaseModel):
    sql: str
    params: list[Any] = Field(default_factory=list)
    source_table: str


def extract_number_after_keywords(text: str) -> int | None:
    match = re.search(r"(?:under|below|less than|<=?)\s*(\d+)", text)
    if not match:
        return None
    return int(match.group(1))


def generate_text2sql_plan(question: str) -> SQLPlan | None:
    lowered = question.lower()
    terms = set(extract_terms(question))

    if "low sugar" in lowered or "sugar" in terms or "healthy" in terms:
        sugar_cap = extract_number_after_keywords(lowered) or 10
        return SQLPlan(
            sql=(
                "SELECT name, category, sugar_grams, calories, bulk_available "
                "FROM products WHERE sugar_grams <= ? ORDER BY sugar_grams ASC LIMIT 10"
            ),
            params=[sugar_cap],
            source_table="products",
        )

    if "ingredients" in terms or "ingredient" in terms or "citrus" in terms:
        target = "citrus" if "citrus" in terms else ""
        if target:
            return SQLPlan(
                sql=(
                    "SELECT p.name AS product_name, i.ingredient_name "
                    "FROM products p "
                    "JOIN product_ingredients pi ON p.id = pi.product_id "
                    "JOIN ingredients i ON i.id = pi.ingredient_id "
                    "WHERE lower(p.name) LIKE ? OR lower(p.category) LIKE ? "
                    "ORDER BY p.name LIMIT 10"
                ),
                params=[f"%{target}%", f"%{target}%"],
                source_table="product_ingredients",
            )

    if "promotion" in terms or "promotions" in terms:
        if "sparkling" in terms:
            return SQLPlan(
                sql=(
                    "SELECT title, details, active FROM promotions "
                    "WHERE active = 1 AND (lower(title) LIKE ? OR lower(details) LIKE ?) "
                    "LIMIT 10"
                ),
                params=["%sparkling%", "%sparkling%"],
                source_table="promotions",
            )
        return SQLPlan(
            sql="SELECT title, details, active FROM promotions WHERE active = 1 LIMIT 10",
            params=[],
            source_table="promotions",
        )

    if "damaged" in terms or ("order" in terms and "policy" in terms):
        return SQLPlan(
            sql=(
                "SELECT title, article_body FROM support_articles "
                "WHERE lower(title) LIKE ? OR lower(article_body) LIKE ? "
                "LIMIT 10"
            ),
            params=["%damaged%", "%damaged%"],
            source_table="support_articles",
        )

    if "bulk" in terms:
        return SQLPlan(
            sql=(
                "SELECT name, category, bulk_available FROM products "
                "WHERE bulk_available = 1 LIMIT 10"
            ),
            params=[],
            source_table="products",
        )

    return None


def run_text2sql(plan: SQLPlan) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(plan.sql, tuple(plan.params)).fetchall()
    return [dict(row) for row in rows]


def retrieve_context(question: str) -> list[dict[str, str]]:
    lowered_question = question.lower()
    terms = extract_terms(question)
    context_rows: list[dict[str, str]] = []

    with get_connection() as conn:
        product_rows = []
        support_rows = []
        promo_rows = []
        ingredient_rows = []

        # Intent-focused retrieval for low sugar and healthy suggestions.
        if "low sugar" in lowered_question or (
            "sugar" in terms and ("low" in lowered_question or "healthy" in terms)
        ):
            product_rows = conn.execute(
                """
                SELECT name, category, sugar_grams, bulk_available
                FROM products
                WHERE sugar_grams <= 10
                ORDER BY sugar_grams ASC
                LIMIT 5
                """
            ).fetchall()

        if not product_rows:
            product_filter, product_params = build_like_conditions(["name", "category"], terms)
            if product_filter:
                product_rows = conn.execute(
                    f"""
                    SELECT name, category, sugar_grams, bulk_available
                    FROM products
                    WHERE {product_filter}
                    LIMIT 5
                    """,
                    product_params,
                ).fetchall()

        # Ingredient-specific retrieval using join table.
        if "ingredient" in terms or "ingredients" in terms or "citrus" in terms:
            ingredient_filter, ingredient_params = build_like_conditions(
                ["p.name", "p.category", "i.ingredient_name"], terms
            )
            if ingredient_filter:
                ingredient_rows = conn.execute(
                    f"""
                    SELECT p.name AS product_name, i.ingredient_name AS ingredient_name
                    FROM products p
                    JOIN product_ingredients pi ON p.id = pi.product_id
                    JOIN ingredients i ON i.id = pi.ingredient_id
                    WHERE {ingredient_filter}
                    LIMIT 5
                    """,
                    ingredient_params,
                ).fetchall()

        promo_filter, promo_params = build_like_conditions(["title", "details"], terms)
        if promo_filter:
            promo_rows = conn.execute(
                f"""
                SELECT title, details
                FROM promotions
                WHERE active = 1 AND ({promo_filter})
                LIMIT 5
                """,
                promo_params,
            ).fetchall()

        support_filter, support_params = build_like_conditions(["title", "article_body", "category"], terms)
        if support_filter:
            support_rows = conn.execute(
                f"""
                SELECT title, article_body
                FROM support_articles
                WHERE {support_filter}
                LIMIT 5
                """,
                support_params,
            ).fetchall()

    for row in product_rows:
        context_rows.append(
            {
                "source_table": "products",
                "snippet": f"{row['name']} ({row['category']}) sugar={row['sugar_grams']}g bulk={row['bulk_available']}",
            }
        )

    for row in ingredient_rows:
        context_rows.append(
            {
                "source_table": "product_ingredients",
                "snippet": f"{row['product_name']} includes ingredient {row['ingredient_name']}",
            }
        )

    for row in support_rows:
        context_rows.append(
            {
                "source_table": "support_articles",
                "snippet": f"{row['title']}: {row['article_body'][:180]}",
            }
        )
    for row in promo_rows:
        context_rows.append(
            {
                "source_table": "promotions",
                "snippet": f"{row['title']}: {row['details']}",
            }
        )

    unique_rows: list[dict[str, str]] = []
    seen_snippets: set[str] = set()
    for row in context_rows:
        if row["snippet"] in seen_snippets:
            continue
        seen_snippets.add(row["snippet"])
        unique_rows.append(row)

    logger.info("retrieval complete terms=%s retrieved_context_count=%s", terms, len(unique_rows))
    return unique_rows[:6]


def offline_answer(question: str, context_rows: list[dict[str, str]]) -> str:
    if not context_rows:
        return "I do not have enough DRINKOO retrieved context to answer that safely."

    formatted_items = "\n".join(f"- {item['snippet']}" for item in context_rows[:3])
    return (
        f"{formatted_items}\n\nIf you need exact policy details, please ask for a specific support topic."
    )


def openrouter_answer(question: str, context_rows: list[dict[str, str]], image_metadata: str) -> str:
    if not OPENROUTER_API_KEY:
        return offline_answer(question, context_rows)

    retrieved_context = "\n".join(
        f"[{item['source_table']}] {item['snippet']}" for item in context_rows
    )
    system_prompt = (
        "You are a DRINKOO assistant. Answer only from retrieved context. "
        "If unknown, say unknown. Do not hallucinate."
    )
    user_prompt = (
        f"Question: {question}\n"
        f"Retrieved context: {retrieved_context or 'none'}\n"
        f"Image metadata: {image_metadata or 'none'}"
    )

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://drinkoo.local",
        "X-Title": "DRINKOO Capstone",
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        logger.error("openrouter call failed error=%s", exc)
        return offline_answer(question, context_rows)


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=80)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    image_metadata: str | None = Field(default="", max_length=500)


@asynccontextmanager
async def lifespan(app: FastAPI):
    del app
    init_database()
    ensure_demo_user()
    cleanup_expired_sessions()
    logger.info("app startup complete")
    yield


app = FastAPI(title="DRINKOO RAG Chatbot", lifespan=lifespan)
templates = Jinja2Templates(directory=str(FRONTEND_DIR))
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


def current_user_id(authorization: str = Header(default="")) -> int:
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", maxsplit=1)[1].strip()
    user_id = get_session_user_id(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> Any:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/signup")
def signup(payload: SignupRequest) -> dict[str, str]:
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (payload.email.lower(),),
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        conn.execute(
            "INSERT INTO users (email, full_name, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (
                payload.email.lower(),
                payload.full_name,
                hash_password(payload.password),
                int(time.time()),
            ),
        )
        conn.commit()
    logger.info("signup success email=%s", payload.email)
    return {"message": "Signup successful"}


@app.post("/api/login")
def login(payload: LoginRequest) -> dict[str, str]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (payload.email.lower(),),
        ).fetchone()

    if row is None or not verify_password(payload.password, row["password_hash"]):
        logger.warning("login failed email=%s", payload.email)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_session(int(row["id"]))
    logger.info("login success email=%s", payload.email)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/api/logout")
def logout(user_id: int = Depends(current_user_id), authorization: str = Header(default="")) -> dict[str, str]:
    del user_id
    token = authorization.split(" ", maxsplit=1)[1].strip()
    delete_session(token)
    return {"message": "Logged out"}


@app.get("/api/status")
def status() -> dict[str, Any]:
    db_ok = False
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1").fetchone()
            db_ok = True
    except Exception as exc:  # noqa: BLE001
        logger.error("db health check failed error=%s", exc)

    rag_ready = SCHEMA_PATH.exists() and SEED_PATH.exists()
    return {
        "api_health": "ok",
        "database_connectivity": "ok" if db_ok else "error",
        "rag_readiness": "ready" if rag_ready else "not_ready",
        "app_version": "1.0.0",
        "environment": os.getenv("APP_ENV", "local"),
    }


@app.get("/api/me")
def me(user_id: int = Depends(current_user_id)) -> dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, email, full_name FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": row["id"], "email": row["email"], "full_name": row["full_name"]}


@app.post("/api/chat")
def chat(payload: ChatRequest, user_id: int = Depends(current_user_id)) -> dict[str, Any]:
    del user_id
    context_rows = retrieve_context(payload.question)

    sql_plan = generate_text2sql_plan(payload.question)
    sql_preview: list[dict[str, Any]] = []
    if sql_plan is not None:
        try:
            sql_preview = run_text2sql(sql_plan)
            for row in sql_preview[:3]:
                context_rows.append(
                    {
                        "source_table": sql_plan.source_table,
                        "snippet": f"Text2SQL row: {row}",
                    }
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("text2sql execution failed error=%s", exc)

    answer = openrouter_answer(payload.question, context_rows, payload.image_metadata or "")

    logger.info(
        "chat processed question_len=%s retrieved_context_count=%s",
        len(payload.question),
        len(context_rows),
    )
    return {
        "answer": answer,
        "retrieved_context": context_rows,
        "source_table": [item["source_table"] for item in context_rows],
        "relevant_sql": sql_plan.sql if sql_plan is not None else "",
        "sql_params": sql_plan.params if sql_plan is not None else [],
        "sql_result_preview": sql_preview[:5],
    }


@app.post("/api/upload")
async def upload_image(
    file: UploadFile = File(...),
    user_id: int = Depends(current_user_id),
) -> dict[str, Any]:
    del user_id

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid content_type")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeded")

    safe_name = f"{int(time.time())}-{secrets.token_hex(8)}-{Path(file.filename or 'image').name}"
    destination = UPLOAD_DIR / safe_name
    destination.write_bytes(content)

    logger.info("upload success content_type=%s size=%s", file.content_type, len(content))
    return {
        "message": "Upload successful",
        "filename": safe_name,
        "content_type": file.content_type,
        "size": len(content),
    }
