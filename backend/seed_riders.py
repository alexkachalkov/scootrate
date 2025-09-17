#!/usr/bin/env python3
"""Seed the database with sample rider records."""

from __future__ import annotations

import random
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DB_PATH = ROOT_DIR / "data" / "top-scoot.sqlite3"

FIRST_NAMES = [
    "Alexei",
    "Maksim",
    "Nikita",
    "Sergei",
    "Timur",
    "Ivan",
    "Dmitri",
    "Pavel",
    "Roman",
    "Egor",
]

LAST_NAMES = [
    "Petrov",
    "Smirnov",
    "Ivanov",
    "Kuznetsov",
    "Popov",
    "Sokolov",
    "Lebedev",
    "Morozov",
    "Volkov",
    "Fedorov",
]

CITIES = [
    "Moscow",
    "Saint Petersburg",
    "Kazan",
    "Novosibirsk",
    "Yekaterinburg",
    "Krasnodar",
    "Sochi",
    "Rostov-on-Don",
    "Chelyabinsk",
    "Vladivostok",
]

STYLES = ["street", "park", "universal"]
LEVELS = ["novice", "amateur", "pro"]


def build_riders() -> list[dict[str, str]]:
    random.seed(42)
    riders: list[dict[str, str]] = []

    for index in range(50):
        first = FIRST_NAMES[index % len(FIRST_NAMES)]
        last = LAST_NAMES[(index // len(FIRST_NAMES)) % len(LAST_NAMES)]
        full_name = f"{first} {last}"
        nickname = f"{first[:3].lower()}{last[:3].lower()}{index + 1:02d}"
        city = CITIES[index % len(CITIES)]
        style = STYLES[index % len(STYLES)]
        level = LEVELS[(index // 10) % len(LEVELS)]

        year = 1999 + (index % 17)
        month = ((index * 3) % 12) + 1
        day = ((index * 7) % 28) + 1
        birthdate = f"{year:04d}-{month:02d}-{day:02d}"

        riders.append(
            {
                "nickname": nickname,
                "fullname": full_name,
                "city": city,
                "birthdate": birthdate,
                "style": style,
                "level": level,
                "email": f"{nickname}@topscoot.test",
            }
        )

    return riders


def seed_riders(db_path: Path) -> int:
    riders = build_riders()
    inserted = 0

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        for rider in riders:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO riders (
                    nickname, fullname, city, birthdate, style, level, socials_json, email
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rider["nickname"],
                    rider["fullname"],
                    rider["city"],
                    rider["birthdate"],
                    rider["style"],
                    rider["level"],
                    "{}",
                    rider["email"],
                ),
            )
            if cur.rowcount:
                inserted += 1
        conn.commit()
    return inserted


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    inserted = seed_riders(DB_PATH)
    print(f"Inserted {inserted} riders into {DB_PATH}")


if __name__ == "__main__":
    main()
