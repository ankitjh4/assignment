"""Compact schema description (allowlist + few-shot prompt) for Text2SQL."""
from __future__ import annotations

from typing import Dict, List


ALLOWED_TABLES: Dict[str, List[str]] = {
    "users": ["id", "email", "full_name", "role", "created_at"],
    "products": [
        "id", "sku", "name", "category", "flavor", "is_sparkling",
        "sugar_g_per_100ml", "calories_per_100ml", "price_cents", "currency",
        "in_stock", "supports_bulk", "image_path", "description", "created_at",
    ],
    "ingredients": ["id", "name", "is_natural", "allergen_flag", "source_country"],
    "product_ingredients": ["product_id", "ingredient_id", "percentage"],
    "orders": ["id", "user_id", "status", "total_cents", "currency", "placed_at", "shipped_at", "is_bulk"],
    "order_items": ["id", "order_id", "product_id", "qty", "unit_price_cents"],
    "promotions": [
        "id", "code", "title", "description", "applies_to_category",
        "discount_pct", "starts_at", "ends_at", "is_active",
    ],
    "support_articles": ["id", "slug", "title", "body", "tags", "updated_at"],
    "chat_sessions": ["id", "user_id", "started_at", "last_message_at", "message_count"],
}


SCHEMA_CARD = """Database: SQLite. Read-only queries only. Use only the tables and columns below.

Tables:
- users(id, email, full_name, role, created_at)
- products(id, sku, name, category, flavor, is_sparkling, sugar_g_per_100ml, calories_per_100ml, price_cents, currency, in_stock, supports_bulk, image_path, description, created_at)
- ingredients(id, name, is_natural, allergen_flag, source_country)
- product_ingredients(product_id, ingredient_id, percentage)
- orders(id, user_id, status, total_cents, currency, placed_at, shipped_at, is_bulk)
- order_items(id, order_id, product_id, qty, unit_price_cents)
- promotions(id, code, title, description, applies_to_category, discount_pct, starts_at, ends_at, is_active)
- support_articles(id, slug, title, body, tags, updated_at)
- chat_sessions(id, user_id, started_at, last_message_at, message_count)

Useful notes:
- products.is_sparkling, products.supports_bulk, products.in_stock and promotions.is_active are 0/1 integers.
- product_ingredients joins products and ingredients many-to-many via product_id and ingredient_id.
- order_items joins orders and products via order_id and product_id.
- Prefer ORDER BY and LIMIT to keep responses small.

Rules:
- Output a single SELECT statement.
- No INSERT, UPDATE, DELETE, DROP, ALTER, ATTACH, PRAGMA.
- No multiple statements (no semicolons mid-query).
- Reference only the tables and columns listed above.

Few-shot examples:

Q: List products with sugar under 4 g per 100ml.
SQL: SELECT id, name, sugar_g_per_100ml FROM products WHERE sugar_g_per_100ml < 4 ORDER BY sugar_g_per_100ml ASC

Q: Show active promotions for citrus category.
SQL: SELECT id, code, title FROM promotions WHERE is_active = 1 AND applies_to_category = 'citrus' ORDER BY id ASC

Q: Top 3 best-selling products by total quantity.
SQL: SELECT p.id, p.name, SUM(oi.qty) AS total_qty FROM order_items oi JOIN products p ON p.id = oi.product_id GROUP BY p.id, p.name ORDER BY total_qty DESC LIMIT 3
"""


def render_schema_card() -> str:
    return SCHEMA_CARD
