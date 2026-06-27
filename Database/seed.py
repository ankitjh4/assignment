#!/usr/bin/env python3
"""Load DRINKOO schema and seed data into the SQLite database."""

import sqlite3
import sys
from pathlib import Path

DB_DIR = Path(__file__).parent
SCHEMA_FILE = DB_DIR / "schema.sql"
SEED_FILE = DB_DIR / "seed.sql"
DEFAULT_DB = DB_DIR.parent / "Backend" / "drinkoo.db"


def load_file(conn: sqlite3.Connection, sql_file: Path) -> None:
    sql = sql_file.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def seed(db_path: Path = DEFAULT_DB, reset: bool = False) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if reset and db_path.exists():
        db_path.unlink()
        print(f"Removed existing database: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    print(f"Loading schema from {SCHEMA_FILE} ...")
    load_file(conn, SCHEMA_FILE)

    print(f"Loading seed data from {SEED_FILE} ...")
    load_file(conn, SEED_FILE)

    cur = conn.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]
    print(f"Database ready at {db_path} — {count} products loaded.")
    conn.close()


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    seed(reset=reset_flag)
