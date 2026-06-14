"""Test that the DRINKOO database schema loads correctly with all required tables."""

from sqlalchemy import inspect, text

from conftest import engine


EXPECTED_TABLES = {
    "users",
    "products",
    "ingredients",
    "product_ingredients",
    "orders",
    "support_articles",
    "promotions",
    "chat_sessions",
}

EXPECTED_COLUMNS = {
    "users": {"id", "email", "hashed_password", "full_name", "is_active", "created_at"},
    "products": {"id", "name", "category", "description", "price", "is_bulk_available",
                 "is_low_sugar", "calories", "stock_quantity"},
    "orders": {"id", "user_id", "product_id", "quantity", "total_price", "status", "created_at"},
    "promotions": {"id", "product_id", "title", "discount_pct", "description", "active",
                   "starts_at", "expires_at"},
    "chat_sessions": {"id", "user_id", "question", "retrieved_context", "answer", "created_at"},
}


def test_all_tables_exist(setup_test_db):
    inspector = inspect(engine)
    actual = set(inspector.get_table_names())
    assert EXPECTED_TABLES.issubset(actual), f"Missing tables: {EXPECTED_TABLES - actual}"


def test_table_count_at_least_six(setup_test_db):
    inspector = inspect(engine)
    assert len(inspector.get_table_names()) >= 6


def test_user_table_columns(setup_test_db):
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("users")}
    assert EXPECTED_COLUMNS["users"].issubset(cols)


def test_products_table_columns(setup_test_db):
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("products")}
    assert EXPECTED_COLUMNS["products"].issubset(cols)


def test_orders_table_columns(setup_test_db):
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("orders")}
    assert EXPECTED_COLUMNS["orders"].issubset(cols)


def test_promotions_table_columns(setup_test_db):
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("promotions")}
    assert EXPECTED_COLUMNS["promotions"].issubset(cols)


def test_chat_sessions_table_columns(setup_test_db):
    inspector = inspect(engine)
    cols = {c["name"] for c in inspector.get_columns("chat_sessions")}
    assert EXPECTED_COLUMNS["chat_sessions"].issubset(cols)


def test_can_insert_and_query_product(db):
    db.execute(
        text("""
            INSERT INTO products (name, category, price, is_bulk_available, is_low_sugar, stock_quantity)
            VALUES ('Test Drink', 'Juice', 1.99, 0, 1, 10)
        """)
    )
    db.commit()
    row = db.execute(text("SELECT name FROM products WHERE name = 'Test Drink'")).fetchone()
    assert row is not None
    assert row[0] == "Test Drink"
