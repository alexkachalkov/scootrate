#!/usr/bin/env python3
"""Seed the database with sample rider records."""

from __future__ import annotations

import os
import random
import mysql.connector
from pathlib import Path

# Get database connection parameters from environment
db_config = {
    'host': os.environ.get("DB_HOST", "scootrate-mariadb-wmclth"),
    'port': int(os.environ.get("DB_PORT", 3306)),
    'user': os.environ.get("DB_USER", "scootrate"),
    'password': os.environ.get("DB_PASSWORD", "secret"),
    'database': os.environ.get("DB_NAME", "scootrate"),
    'charset': 'utf8mb4'
}

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


def seed_riders() -> int:
    riders = build_riders()
    inserted = 0

    conn = mysql.connector.connect(**db_config)
    try:
        cursor = conn.cursor()
        
        for rider in riders:
            cursor.execute(
                "SELECT id FROM riders WHERE nickname = %s",
                (rider["nickname"],)
            )
            if cursor.fetchone():
                continue
                
            cursor.execute(
                """
                INSERT IGNORE INTO riders (
                    nickname, fullname, city, birthdate, style, level, socials_json, email
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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
            if cursor.rowcount:
                inserted += 1
                
        conn.commit()
        cursor.close()
    finally:
        conn.close()
        
    return inserted


def main() -> None:
    inserted = seed_riders()
    print(f"Inserted {inserted} riders")


if __name__ == "__main__":
    main()
