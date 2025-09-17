#!/usr/bin/env python3
"""Simple SQLite migration runner for Top Scoot."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DEFAULT_DB = ROOT_DIR / "data" / "top-scoot.sqlite3"
MIGRATIONS_DIR = BASE_DIR / "migrations"


def ensure_schema_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        """
    )


def applied_migrations(conn: sqlite3.Connection) -> set[str]:
    cur = conn.execute("SELECT filename FROM schema_migrations")
    return {row[0] for row in cur.fetchall()}


def apply_migration(conn: sqlite3.Connection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.execute("INSERT INTO schema_migrations (filename) VALUES (?)", (path.name,))
    conn.commit()


def run_migrations(db_path: Path) -> None:
    if not MIGRATIONS_DIR.exists():
        raise SystemExit(f"Migrations directory not found: {MIGRATIONS_DIR}")

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        ensure_schema_table(conn)
        already_applied = applied_migrations(conn)

        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in already_applied:
                continue
            apply_migration(conn, path)
            print(f"Applied migration {path.name}")

        conn.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SQLite migrations.")
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DB,
        help=f"Path to SQLite database file (default: {DEFAULT_DB})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.database.parent.mkdir(parents=True, exist_ok=True)
    run_migrations(args.database)


if __name__ == "__main__":
    main()
