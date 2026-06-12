# DRINKOO Database

SQLite database for the DRINKOO RAG chatbot.

## Files

- `schema.sql` - canonical table creation script (9 tables, exceeds the 6-table minimum). Auto-applied at app startup via `Backend/database.py`.
- `seed.sql` - idempotent seed data (~20 products, 25 ingredients, 7 promotions, 8 support articles, 5 demo orders, 2 chat sessions).
- `text2sql_samples.json` - 14 natural-language questions with expected SQL and row-signatures used by the Text2SQL correctness test (`Tests/test_text2sql.py`).

## Tables

| Table | Purpose |
| --- | --- |
| `users` | Authenticated customers and admins. Passwords are bcrypt-hashed. |
| `products` | The DRINKOO catalog. Includes sugar, calories, sparkling flag, bulk support. |
| `ingredients` | Ingredient master with allergen flag and source country. |
| `product_ingredients` | Many-to-many between products and ingredients with percentage composition. |
| `orders` | Customer orders with status and total. |
| `order_items` | Order line items joining orders to products. |
| `promotions` | Marketing promotions with active flag and category targeting. |
| `support_articles` | Customer support knowledge base used by RAG retrieval. |
| `chat_sessions` | Conversation log header per user. |

## How to create, reset, seed

```bash
# from inside the assignment/ folder
python scripts/seed_db.py        # resets and seeds drinkoo.db
```

Or let the FastAPI app build the schema on first boot:

```bash
uvicorn Backend.app:app --reload --port 8000
```

The application calls `init_db_if_needed()` during the FastAPI lifespan, which applies `schema.sql` and `seed.sql` if the `users` table is missing or empty.

## Text2SQL correctness target

`Tests/test_text2sql.py` runs every sample in `text2sql_samples.json`. The test passes when correctness >= 90%. Results land in `Reports/text2sql-results.md`.
