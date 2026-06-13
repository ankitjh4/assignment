"""Tests for database schema loading."""
import sqlite3
from pathlib import Path


EXPECTED_TABLES = [
    "users",
    "products",
    "ingredients",
    "product_ingredients",
    "orders",
    "support_articles",
    "promotions",
    "chat_sessions",
]


def test_schema_loads_without_error():
    schema_sql = Path("Database/schema.sql").read_text()
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def test_all_tables_created():
    schema_sql = Path("Database/schema.sql").read_text()
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_sql)
    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    conn.close()
    for table in EXPECTED_TABLES:
        assert table in tables, f"Table '{table}' missing from schema"


def test_products_table_columns():
    schema_sql = Path("Database/schema.sql").read_text()
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_sql)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(products)")}
    conn.close()
    for col in ("id", "name", "category", "description", "price", "sugar_grams", "is_bulk_available"):
        assert col in cols, f"Column '{col}' missing from products table"


def test_users_table_has_password_hash():
    schema_sql = Path("Database/schema.sql").read_text()
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema_sql)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
    conn.close()
    assert "password_hash" in cols
    assert "email" in cols


def test_foreign_keys_declared():
    schema_path = Path("Database/schema.sql")
    content = schema_path.read_text().lower()
    assert "references" in content, "Schema should declare foreign keys with REFERENCES"
