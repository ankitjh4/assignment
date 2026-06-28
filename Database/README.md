# DRINKOO Database Documentation

## Overview

The DRINKOO database is built with SQLite and manages:

- User accounts and authentication
- Product inventory (SKUs)
- Ingredient relationships
- Orders and transactions
- Support articles for RAG retrieval
- Promotions and chat sessions

## Schema

### Core Tables

**users**

- Stores user authentication data
- Fields: id, username, email, password_hash, created_at, updated_at

**products** (SKU Management)

- DRINKOO drink products
- Fields: id, sku, name, description, unit_volume_ml, category, price_cents
- Constraint: unit_volume_ml must be in (1, 1.5, 2, 4, 6, 8, 12)

**ingredients**

- Base ingredients used in products
- Fields: id, name, description, allergen_flag

**product_ingredients**

- Join table mapping products to ingredients with quantities
- Fields: id, product_id, ingredient_id, quantity_grams

**orders**

- Customer orders
- Fields: id, user_id, product_id, quantity, total_price_cents, order_status

**support_articles**

- Documentation for RAG retrieval (chatbot knowledge base)
- Fields: id, title, content, topic, created_at, updated_at

### Optional Tables

**promotions**

- Marketing campaigns
- Fields: id, name, description, discount_percent, start_date, end_date

**chat_sessions**

- Conversation history tracking
- Fields: id, user_id, session_key, created_at, updated_at

## Setup Instructions

### 1. Create Database

Run the data loader script:

```bash
python scripts/load_data.py
```

This will:

- Create `Database/drinkoo.db`
- Load schema from `Database/schema.sql`
- Seed 6 products, 10 ingredients, 2 users, and 6 support articles
- Display Text2SQL validation samples

### 2. Reset Database

To start fresh:

```bash
python scripts/load_data.py  # Automatically removes old DB
```

Or manually:

```bash
rm Database/drinkoo.db
python scripts/load_data.py
```

### 3. Verify Data

Connect to the database:

```bash
sqlite3 Database/drinkoo.db
```

Sample queries:

```sql
-- List all products
SELECT sku, name, unit_volume_ml, price_cents FROM products;

-- Show products with ingredients
SELECT p.name, i.name as ingredient, pi.quantity_grams
FROM products p
JOIN product_ingredients pi ON p.id = pi.product_id
JOIN ingredients i ON pi.ingredient_id = i.id;

-- Get allergen information
SELECT p.name, i.name as allergen
FROM products p
JOIN product_ingredients pi ON p.id = pi.product_id
JOIN ingredients i ON pi.ingredient_id = i.id
WHERE i.allergen_flag = 1;
```

## Text2SQL Validation

The data loader includes 10 sample natural language questions with expected SQL outputs for validating Text2SQL accuracy. Target: ≥90% correctness.

Samples include:

- Product category filters
- Ingredient lookups
- Multi-table joins
- Allergen queries
- Sorting and numeric comparisons
- Support article retrieval

## Indexes

The schema includes optimized indexes for:

- Product lookups by SKU
- Category searches
- User order history
- Product-ingredient relationships
- Support article topic searches

## Foreign Keys

All relationships maintain referential integrity:

- orders → users, products
- product_ingredients → products, ingredients
- chat_sessions → users

Cascade delete ensures orphaned data is cleaned up automatically.

## Volume Constraints

Products must have volume in milliliters: **1, 1.5, 2, 4, 6, 8, or 12 mL**

This is enforced by SQLite CHECK constraint on `products.unit_volume_ml`.

## Development Notes

- All timestamps default to `CURRENT_TIMESTAMP`
- Price stored in cents (e.g., $3.50 = 350)
- Product SKUs are unique and immutable
- Usernames and emails are unique per user
