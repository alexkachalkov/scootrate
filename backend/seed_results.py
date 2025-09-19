#!/usr/bin/env python3
"""Seed the database with sample results and recalculate season points."""

from __future__ import annotations

import os
import mysql.connector
from pathlib import Path
from typing import Iterable

from season import recalculate_season_points

# Get database connection parameters from environment
db_config = {
    'host': os.environ.get("DB_HOST", "scootrate-mariadb-wmclth"),
    'port': int(os.environ.get("DB_PORT", 3306)),
    'user': os.environ.get("DB_USER", "scootrate"),
    'password': os.environ.get("DB_PASSWORD", "secret"),
    'database': os.environ.get("DB_NAME", "scootrate"),
    'charset': 'utf8mb4'
}

POINTS_TABLE = {
    "international": {
        "place": {1: 400, 2: 300, 3: 220},
        "finalist": 100,
        "participant": 20,
    },
    "national": {
        "place": {1: 300, 2: 220, 3: 160},
        "finalist": 80,
        "participant": 15,
    },
    "regional": {
        "place": {1: 200, 2: 140, 3: 100},
        "finalist": 50,
        "participant": 10,
    },
    "local": {
        "place": {1: 120, 2: 80, 3: 60},
        "finalist": 30,
        "participant": 5,
    },
}


def bonus_multiplier(participants_count: int | None) -> float:
    if participants_count is None:
        return 1.0
    if participants_count > 60:
        return 1.2
    if participants_count > 30:
        return 1.1
    return 1.0


def calculate_points(
    level: str,
    place: int | None,
    is_finalist: bool,
    is_participant: bool,
    participants_count: int | None,
) -> int:
    base_points = 0
    table = POINTS_TABLE[level]

    if place in table["place"]:
        base_points = table["place"][place]
    elif is_finalist:
        base_points = table["finalist"]
    elif is_participant:
        base_points = table["participant"]

    total = base_points * bonus_multiplier(participants_count)
    return int(round(total))


def fetch_rider_ids(conn: mysql.connector.connection.MySQLConnection) -> list[int]:
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM riders ORDER BY id")
    result = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return result


def fetch_events(conn: mysql.connector.connection.MySQLConnection) -> list[tuple[int, str, int | None]]:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, level, participants_count FROM events ORDER BY date_start"
    )
    result = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
    cursor.close()
    return result


def chunk(iterable: Iterable[int], size: int) -> list[list[int]]:
    items = list(iterable)
    chunks: list[list[int]] = []
    for start in range(0, len(items), size):
        chunks.append(items[start : start + size])
    return chunks


def seed_results() -> int:
    inserted = 0
    conn = mysql.connector.connect(**db_config)
    try:
        rider_ids = fetch_rider_ids(conn)
        events = fetch_events(conn)
        if not rider_ids or not events:
            return 0

        rider_cycle = rider_ids * 2  # reuse riders across events
        rider_sets = chunk(rider_cycle, 20)

        for index, (event_id, level, participants_count) in enumerate(events):
            riders_for_event = rider_sets[index] if index < len(rider_sets) else rider_ids
            for position, rider_id in enumerate(riders_for_event, start=1):
                place: int | None
                is_finalist = False
                is_participant = True

                if position <= 3:
                    place = position
                elif position <= 8:
                    place = position
                    is_finalist = True
                else:
                    place = None

                points = calculate_points(level, place, is_finalist, is_participant, participants_count)

                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO results (
                        event_id, rider_id, place, is_finalist, is_participant, points, comment
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        place = VALUES(place),
                        is_finalist = VALUES(is_finalist),
                        is_participant = VALUES(is_participant),
                        points = VALUES(points),
                        comment = VALUES(comment)
                    """,
                    (
                        event_id,
                        rider_id,
                        place,
                        int(is_finalist),
                        int(is_participant),
                        points,
                        "Seeded result",
                    ),
                )
                inserted += 1
                cursor.close()
        conn.commit()

        # Recalculate season points
        recalculate_season_points(conn)
        conn.commit()
    finally:
        conn.close()
    return inserted


def main() -> None:
    inserted = seed_results()
    print(f"Inserted/updated {inserted} results and recalculated season points")


if __name__ == "__main__":
    main()
