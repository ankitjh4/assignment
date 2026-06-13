-- DRINKOO Database Schema
-- Run via: python Database/seed.py  (which calls init_db then seeds)

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    is_available INTEGER NOT NULL DEFAULT 1,
    sugar_grams REAL NOT NULL DEFAULT 0,
    is_bulk_available INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    allergen_info TEXT
);

CREATE TABLE IF NOT EXISTS product_ingredients (
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    quantity TEXT NOT NULL,
    PRIMARY KEY (product_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS support_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS promotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    discount_percent REAL NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    question TEXT NOT NULL,
    context_used TEXT,
    answer TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
