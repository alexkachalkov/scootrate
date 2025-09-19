#!/usr/bin/env python3
"""MariaDB migration runner for Top Scoot."""

from __future__ import annotations

import argparse
import mysql.connector
from pathlib import Path
import os
import re

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
    sql = re.sub(r"TEXT(\s+COLLATE\s+NOCASE)", r"VARCHAR(255)", sql)
    sql = sql.replace("TEXT", "TEXT")
    sql = sql.replace("DEFAULT (datetime('now'))", "DEFAULT CURRENT_TIMESTAMP")
    sql = sql.replace("PRAGMA foreign_keys = ON;", "")
    sql = sql.replace("BEGIN TRANSACTION;", "START TRANSACTION;")
    sql = sql.replace("COMMIT;", "")
    
    # Handle CHECK constraints properly
    sql = re.sub(r"CHECK\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s+IN\s*\(\s*'[^']*'(?:\s*,\s*'[^']*')*\s*\)\s*\)", 
                 lambda m: m.group(0).replace(")", ")"), sql)
    
    # Remove COLLATE NOCASE as it's not needed in the same way in MariaDB
    sql = sql.replace(" COLLATE NOCASE", "")
    
    return sql

def apply_migration(conn: mysql.connector.connection.MySQLConnection, path: Path) -> None:
    cursor = conn.cursor()
    
    # Read and convert the SQL
    sql = path.read_text(encoding="utf-8")
    converted_sql = convert_sqlite_to_mariadb(sql)
    
    # Split into statements
    statements = [stmt.strip() for stmt in converted_sql.split(";") if stmt.strip()]
    for statement in statements:
        statement = statement.strip()
        if not statement:
            continue
        if statement.upper().startswith("START TRANSACTION") or statement.upper().startswith("COMMIT"):
            continue
        if statement.upper().startswith("PRAGMA"):
            continue
        try:
            cursor.execute(statement)
        except mysql.connector.Error as e:
            print(f"Error executing statement: {statement[:100]}...")
            print(f"Error: {e}")
            raise
    
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

        # Look for MariaDB-specific migrations first, fallback to generic ones
        migration_files = sorted(MIGRATIONS_DIR.glob("*_mariadb.sql"))
        if not migration_files:
            migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
            
        for path in migration_files:
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