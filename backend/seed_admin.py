#!/usr/bin/env python3
"""Seed the database with default admin/editor users."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import bcrypt

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DB_PATH = ROOT_DIR / "data" / "top-scoot.sqlite3"

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


def seed_users(db_path: Path) -> list[str]:
    created: list[str] = []

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        for user in DEFAULT_USERS:
            email = user["email"]
            cur = conn.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                continue
            password_hash = hash_password(user["password"])
            conn.execute(
                """
                INSERT INTO users (email, password_hash, role)
                VALUES (?, ?, ?)
                """,
                (email, password_hash, user["role"]),
            )
            conn.commit()
            created.append(email)
    return created


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    created = seed_users(DB_PATH)
    if created:
        for email in created:
            print(f"Created user {email}")
    else:
        print("Users already exist, nothing created")


if __name__ == "__main__":
    main()
