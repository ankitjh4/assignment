#!/usr/bin/env python3
"""
DRINKOO Text2SQL Correctness Checker
=====================================
Runs the 10 expected SQL queries from text2sql_checks.md directly against the
SQLite database and reports a correctness score.

A query is PASS if:
  - It executes without error
  - It returns at least 1 row
  - The result contains the expected columns

Usage:
  python Database/test_text2sql.py
  python Database/test_text2sql.py --db path/to/drinkoo.db --verbose
"""

import argparse
import sqlite3
import sys
from pathlib import Path

DB_DEFAULT = Path(__file__).parent.parent / "Backend" / "drinkoo.db"

# ---------------------------------------------------------------------------
# 10 test cases: (question, sql, expected_columns, description)
# ---------------------------------------------------------------------------
CHECKS = [
    (
        "Which DRINKOO products are low sugar?",
        """
        SELECT id, name, category, calories, price
        FROM products
        WHERE is_low_sugar = 1
        ORDER BY name
        """,
        {"id", "name", "category", "calories", "price"},
        "Products table filtered by is_low_sugar = 1",
    ),
    (
        "What ingredients are used in the citrus drinks?",
        """
        SELECT DISTINCT i.name, i.description, i.is_allergen
        FROM ingredients i
        JOIN product_ingredients pi ON i.id = pi.ingredient_id
        JOIN products p ON pi.product_id = p.id
        WHERE p.name LIKE '%Citrus%' OR p.category LIKE '%citrus%'
        """,
        {"name", "description", "is_allergen"},
        "Ingredients joined with product_ingredients for citrus products",
    ),
    (
        "Are there active promotions for sparkling beverages?",
        """
        SELECT pr.title, pr.discount_pct, pr.description, pr.expires_at, p.name AS product_name
        FROM promotions pr
        LEFT JOIN products p ON pr.product_id = p.id
        WHERE pr.active = 1
          AND (p.category = 'Sparkling Water' OR pr.description LIKE '%sparkling%')
        """,
        {"title", "discount_pct", "description", "expires_at", "product_name"},
        "Active promotions for sparkling water category",
    ),
    (
        "What should a customer do if an order arrives damaged?",
        """
        SELECT title, content
        FROM support_articles
        WHERE title LIKE '%damaged%' OR content LIKE '%damaged%'
        ORDER BY id
        """,
        {"title", "content"},
        "Support articles matching keyword 'damaged'",
    ),
    (
        "Which products are available for bulk orders?",
        """
        SELECT id, name, category, price, stock_quantity
        FROM products
        WHERE is_bulk_available = 1
        ORDER BY name
        """,
        {"id", "name", "category", "price", "stock_quantity"},
        "Products with is_bulk_available = 1",
    ),
    (
        "What is the calorie count for energy drinks?",
        """
        SELECT name, calories, is_low_sugar
        FROM products
        WHERE category = 'Energy Drink'
        ORDER BY calories DESC
        """,
        {"name", "calories", "is_low_sugar"},
        "Energy drinks with calorie counts",
    ),
    (
        "Show me all active promotions with their discounts.",
        """
        SELECT pr.title, pr.discount_pct, pr.description, pr.expires_at, p.name AS product_name
        FROM promotions pr
        LEFT JOIN products p ON pr.product_id = p.id
        WHERE pr.active = 1
        ORDER BY pr.discount_pct DESC
        """,
        {"title", "discount_pct", "description", "expires_at", "product_name"},
        "All active promotions ordered by discount",
    ),
    (
        "What are the ingredients in the Green Detox juice?",
        """
        SELECT i.name, i.description, pi.quantity_mg
        FROM ingredients i
        JOIN product_ingredients pi ON i.id = pi.ingredient_id
        JOIN products p ON pi.product_id = p.id
        WHERE p.name = 'Green Detox'
        """,
        {"name", "description", "quantity_mg"},
        "Ingredients for the Green Detox product",
    ),
    (
        "How do I cancel my subscription?",
        """
        SELECT title, content
        FROM support_articles
        WHERE title LIKE '%cancel%' OR content LIKE '%cancel%'
        ORDER BY id
        """,
        {"title", "content"},
        "Support articles matching keyword 'cancel'",
    ),
    (
        "What coconut water products does DRINKOO sell?",
        """
        SELECT id, name, description, price, calories, is_low_sugar, stock_quantity
        FROM products
        WHERE category = 'Coconut Water' OR name LIKE '%Coconut%'
        """,
        {"id", "name", "description", "price", "calories", "is_low_sugar", "stock_quantity"},
        "Products in Coconut Water category or with 'Coconut' in name",
    ),
]

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def run_checks(db_path: Path, verbose: bool = False) -> int:
    if not db_path.exists():
        print(f"{RED}ERROR: Database not found at {db_path}{RESET}")
        print("Run:  python Database/seed.py")
        return 1

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    passed = 0
    failed = 0
    results = []

    print(f"\n{BOLD}DRINKOO Text2SQL Correctness Check{RESET}")
    print(f"Database: {db_path}")
    print("=" * 60)

    for i, (question, sql, expected_cols, description) in enumerate(CHECKS, 1):
        status = "PASS"
        detail = ""
        rows = []

        try:
            cur = conn.execute(sql.strip())
            rows = cur.fetchall()
            actual_cols = {d[0] for d in cur.description} if cur.description else set()

            if len(rows) == 0:
                status = "FAIL"
                detail = "Query returned 0 rows — check seed data"
            else:
                missing = expected_cols - actual_cols
                if missing:
                    status = "FAIL"
                    detail = f"Missing columns: {missing}"

        except sqlite3.Error as exc:
            status = "FAIL"
            detail = f"SQL error: {exc}"

        color = GREEN if status == "PASS" else RED
        print(f"\n{color}[{status}]{RESET}  Q{i}: {question}")
        print(f"        {description}")

        if status == "PASS":
            print(f"        ✓ {len(rows)} row(s) returned")
            passed += 1
            if verbose and rows:
                print(f"        Sample: {dict(rows[0])}")
        else:
            print(f"        ✗ {detail}")
            failed += 1

        results.append((status, question, detail))

    conn.close()

    # Summary
    total    = len(CHECKS)
    pct      = (passed / total) * 100
    threshold = 90.0
    color    = GREEN if pct >= threshold else RED

    print("\n" + "=" * 60)
    print(f"{BOLD}Results: {passed}/{total} passed ({pct:.0f}%){RESET}")
    print(f"Threshold: {threshold:.0f}%  →  {color}{'PASS ✓' if pct >= threshold else 'FAIL ✗'}{RESET}")

    if failed:
        print(f"\n{YELLOW}Failed queries:{RESET}")
        for status, q, detail in results:
            if status == "FAIL":
                print(f"  • {q}")
                print(f"    {detail}")

    return 0 if pct >= threshold else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DRINKOO Text2SQL correctness checker")
    parser.add_argument("--db",      default=str(DB_DEFAULT), help="Path to drinkoo.db")
    parser.add_argument("--verbose", action="store_true",     help="Show sample rows for passing queries")
    args = parser.parse_args()

    sys.exit(run_checks(Path(args.db), verbose=args.verbose))
