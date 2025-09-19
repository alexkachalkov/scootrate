"""SQLite helpers for Flask application."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from flask import Flask, current_app, g

from backend.config import validate_database_config


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    # Validate database configuration on app initialization
    database_path = Path(app.config["DATABASE_PATH"])
    validate_database_config(database_path)


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE_PATH"])
        readonly = bool(current_app.config.get("DATABASE_READONLY"))

        if not readonly:
            database_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(database_path)
        else:
            if not database_path.exists():
                raise FileNotFoundError(f"SQLite database not found: {database_path}")
            uri = f"file:{database_path}?mode=ro"
            conn = sqlite3.connect(uri, uri=True)

        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db  # type: ignore[return-value]


def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()
