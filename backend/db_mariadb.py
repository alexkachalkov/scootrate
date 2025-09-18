"""MariaDB helpers for Flask application."""

from __future__ import annotations

import mysql.connector
from typing import Any
from flask import Flask, current_app, g
from config import validate_database_config

def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    # Validate database configuration on app initialization
    # We'll skip SQLite validation for MariaDB setup
    pass

def get_db() -> mysql.connector.connection.MySQLConnection:
    if "db" not in g:
        # Get database connection parameters from environment
        db_config = {
            'host': current_app.config.get("DB_HOST", "scootrate-mariadb-wmclth"),
            'port': current_app.config.get("DB_PORT", 3306),
            'user': current_app.config.get("DB_USER", "scootrate"),
            'password': current_app.config.get("DB_PASSWORD", "secret"),
            'database': current_app.config.get("DB_NAME", "scootrate"),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
        conn = mysql.connector.connect(**db_config)
        g.db = conn
    return g.db

def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()