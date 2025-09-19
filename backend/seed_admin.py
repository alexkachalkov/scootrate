#!/usr/bin/env python3
"""Seed the database with default admin/editor users."""

from __future__ import annotations

import os
import mysql.connector
from pathlib import Path

import bcrypt

# Get database connection parameters from environment
db_config = {
    'host': os.environ.get("DB_HOST", "scootrate-mariadb-wmclth"),
    'port': int(os.environ.get("DB_PORT", 3306)),
    'user': os.environ.get("DB_USER", "scootrate"),
    'password': os.environ.get("DB_PASSWORD", "secret"),
    'database': os.environ.get("DB_NAME", "scootrate"),
    'charset': 'utf8mb4'
}

DEFAULT_USERS = [
    {
        "email": os.environ.get("TOPSCOOT_ADMIN_EMAIL", "admin@topscoot.test"),
        "password": os.environ.get("TOPSCOOT_ADMIN_PASSWORD", "changeme123"),
        "role": os.environ.get("TOPSCOOT_ADMIN_ROLE", "admin"),
    },
    {
        "email": os.environ.get("TOPSCOOT_EDITOR_EMAIL", "editor@topscoot.test"),
        "password": os.environ.get("TOPSCOOT_EDITOR_PASSWORD", "changeme123"),
        "role": "editor",
    },
]


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def seed_users() -> list[str]:
    created: list[str] = []
    
    conn = mysql.connector.connect(**db_config)
    try:
        cursor = conn.cursor()
        
        for user in DEFAULT_USERS:
            email = user["email"]
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                continue
            password_hash = hash_password(user["password"])
            cursor.execute(
                """
                INSERT INTO users (email, password_hash, role)
                VALUES (%s, %s, %s)
                """,
                (email, password_hash, user["role"]),
            )
            conn.commit()
            created.append(email)
            
        cursor.close()
    finally:
        conn.close()
        
    return created


def main() -> None:
    created = seed_users()
    if created:
        for email in created:
            print(f"Created user {email}")
    else:
        print("Users already exist, nothing created")


if __name__ == "__main__":
    main()
