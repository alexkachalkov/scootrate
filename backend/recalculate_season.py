#!/usr/bin/env python3
"""Utility script to recalculate rolling season points."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from season import recalculate_season_points

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DB_PATH = ROOT_DIR / "data" / "top-scoot.sqlite3"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        recalculate_season_points(conn)
        conn.commit()
    print("Season points recalculated")


if __name__ == "__main__":
    main()
