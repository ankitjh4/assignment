#!/usr/bin/env python3
"""Reset and seed the DRINKOO SQLite database."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_path() -> None:
    here = Path(__file__).resolve().parent.parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))


def main() -> int:
    _ensure_path()
    from Backend.database import reset_db  # noqa: WPS433  (deferred import to ensure path)

    reset_db()
    print("DRINKOO database reset and seeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
