#!/usr/bin/env python3
"""MariaDB migration runner for Top Scoot."""

from __future__ import annotations

import argparse
import mysql.connector
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
MIGRATIONS_DIR = BASE_DIR / "migrations"

def get_db_connection():
    """Create a database connection to MariaDB."""
    db_config = {
        'host': os.environ.get("DB_HOST", "scootrate-mariadb-wmclth"),
        'port': int(os.environ.get("DB_PORT", 3306)),
        'user': os.environ.get("DB_USER", "scootrate"),
        'password': os.environ.get("DB_PASSWORD", "secret"),
        'database': os.environ.get("DB_NAME", "scootrate"),
        'charset': 'utf8mb4'
    }
    
    return mysql.connector.connect(**db_config)

def ensure_schema_table(conn: mysql.connector.connection.MySQLConnection) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL UNIQUE,
            applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()

def applied_migrations(conn: mysql.connector.connection.MySQLConnection) -> set[str]:
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM schema_migrations")
    result = {row[0] for row in cursor.fetchall()}
    cursor.close()
    return result

def convert_sqlite_to_mariadb(sql: str) -> str:
    """Convert SQLite syntax to MariaDB syntax."""
    # Replace SQLite-specific syntax with MariaDB equivalents
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "INT AUTO_INCREMENT PRIMARY KEY")
    sql = sql.replace("TEXT", "TEXT")
    sql = sql.replace("DEFAULT (datetime('now'))", "DEFAULT CURRENT_TIMESTAMP")
    sql = sql.replace("PRAGMA foreign_keys = ON;", "")
    sql = sql.replace("BEGIN TRANSACTION;", "START TRANSACTION;")
    sql = sql.replace("COMMIT;", "")
    
    # Remove SQLite-specific CHECK constraints if needed
    # This is a simplified conversion - you may need to adjust based on your specific needs
    return sql

def apply_migration(conn: mysql.connector.connection.MySQLConnection, path: Path) -> None:
    cursor = conn.cursor()
    
    # Read and convert the SQL
    sql = path.read_text(encoding="utf-8")
    converted_sql = convert_sqlite_to_mariadb(sql)
    
    # Execute each statement separately
    statements = [stmt.strip() for stmt in converted_sql.split(";") if stmt.strip()]
    for statement in statements:
        if statement.upper().startswith("START TRANSACTION") or statement.upper().startswith("COMMIT"):
            continue
        cursor.execute(statement)
    
    # Record the migration
    cursor.execute("INSERT INTO schema_migrations (filename) VALUES (%s)", (path.name,))
    conn.commit()
    cursor.close()

def run_migrations() -> None:
    if not MIGRATIONS_DIR.exists():
        raise SystemExit(f"Migrations directory not found: {MIGRATIONS_DIR}")

    conn = get_db_connection()
    try:
        ensure_schema_table(conn)
        already_applied = applied_migrations(conn)

        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in already_applied:
                print(f"Migration {path.name} already applied, skipping")
                continue
            print(f"Applying migration {path.name}")
            apply_migration(conn, path)
            print(f"Applied migration {path.name}")

    finally:
        conn.close()

def main() -> None:
    run_migrations()

if __name__ == "__main__":
    main()