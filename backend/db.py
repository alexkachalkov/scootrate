"""SQLite helpers for Flask application."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, current_app, g


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE_PATH"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db  # type: ignore[return-value]


def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()
