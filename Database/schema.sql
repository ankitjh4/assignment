-- DRINKOO Database Schema
-- SQLite dialect. Coherent 9-table design (>= 6 required) that supports
-- grounded RAG retrieval AND Text2SQL evaluation queries.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    email           TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    full_name       TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'customer',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    sku                      TEXT NOT NULL UNIQUE,
    name                     TEXT NOT NULL,
    category                 TEXT NOT NULL,
    flavor                   TEXT,
    is_sparkling             INTEGER NOT NULL DEFAULT 0,
    sugar_g_per_100ml        REAL NOT NULL DEFAULT 0,
    calories_per_100ml       INTEGER NOT NULL DEFAULT 0,
    price_cents              INTEGER NOT NULL,
    currency                 TEXT NOT NULL DEFAULT 'USD',
    in_stock                 INTEGER NOT NULL DEFAULT 1,
    supports_bulk            INTEGER NOT NULL DEFAULT 0,
    image_path               TEXT,
    description              TEXT,
    created_at               TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_sparkling ON products(is_sparkling);

CREATE TABLE IF NOT EXISTS ingredients (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    is_natural      INTEGER NOT NULL DEFAULT 1,
    allergen_flag   INTEGER NOT NULL DEFAULT 0,
    source_country  TEXT
);

CREATE TABLE IF NOT EXISTS product_ingredients (
    product_id     INTEGER NOT NULL,
    ingredient_id  INTEGER NOT NULL,
    percentage     REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (product_id, ingredient_id),
    FOREIGN KEY (product_id)    REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'placed',
    total_cents     INTEGER NOT NULL DEFAULT 0,
    currency        TEXT NOT NULL DEFAULT 'USD',
    placed_at       TEXT NOT NULL DEFAULT (datetime('now')),
    shipped_at      TEXT,
    is_bulk         INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id);

CREATE TABLE IF NOT EXISTS order_items (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id          INTEGER NOT NULL,
    product_id        INTEGER NOT NULL,
    qty               INTEGER NOT NULL DEFAULT 1,
    unit_price_cents  INTEGER NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);

CREATE TABLE IF NOT EXISTS promotions (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    code                 TEXT NOT NULL UNIQUE,
    title                TEXT NOT NULL,
    description          TEXT NOT NULL,
    applies_to_category  TEXT,
    discount_pct         INTEGER NOT NULL DEFAULT 0,
    starts_at            TEXT NOT NULL,
    ends_at              TEXT NOT NULL,
    is_active            INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_promotions_active ON promotions(is_active);

CREATE TABLE IF NOT EXISTS support_articles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    slug        TEXT NOT NULL UNIQUE,
    title       TEXT NOT NULL,
    body        TEXT NOT NULL,
    tags        TEXT,
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL,
    started_at       TEXT NOT NULL DEFAULT (datetime('now')),
    last_message_at  TEXT,
    message_count    INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
