from sqlalchemy import inspect

from Backend.database import engine


REQUIRED_TABLES = {
    "users",
    "products",
    "ingredients",
    "product_ingredients",
    "orders",
    "order_items",
    "promotions",
    "support_articles",
    "chat_sessions",
}


def test_schema_has_all_required_tables(client):
    insp = inspect(engine)
    actual = set(insp.get_table_names())
    missing = REQUIRED_TABLES - actual
    assert not missing, f"missing tables: {missing}"
    assert len(actual & REQUIRED_TABLES) >= 6


def test_seed_data_loaded(client):
    response = client.get("/api/catalog/products")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 6
    assert any("Citrus Zing" == p["name"] for p in data["products"])


def test_promotions_endpoint(client):
    response = client.get("/api/catalog/promotions?only_active=true")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert all(p["is_active"] for p in data["promotions"])
