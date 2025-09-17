#!/usr/bin/env python3
"""Seed the database with sample events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DB_PATH = ROOT_DIR / "data" / "top-scoot.sqlite3"


@dataclass
class EventSeed:
    name: str
    start_offset_days: int
    duration_days: int
    city: str
    level: str
    participants_count: int
    style: str | None
    has_best_trick: bool
    source_url: str
    organizer_contact: str
    status: str


SEEDS: list[EventSeed] = [
    EventSeed(
        name="Moscow Spring Jam",
        start_offset_days=-40,
        duration_days=1,
        city="Moscow",
        level="local",
        participants_count=42,
        style="street",
        has_best_trick=True,
        source_url="https://topscoot.test/events/moscow-spring-jam",
        organizer_contact="springjam@topscoot.test",
        status="published",
    ),
    EventSeed(
        name="Volga Regional Cup",
        start_offset_days=-75,
        duration_days=2,
        city="Kazan",
        level="regional",
        participants_count=36,
        style="park",
        has_best_trick=False,
        source_url="https://topscoot.test/events/volga-regional",
        organizer_contact="volga@topscoot.test",
        status="published",
    ),
    EventSeed(
        name="Northern Lights Invitational",
        start_offset_days=-20,
        duration_days=3,
        city="Saint Petersburg",
        level="international",
        participants_count=68,
        style="universal",
        has_best_trick=True,
        source_url="https://topscoot.test/events/northern-lights",
        organizer_contact="lights@topscoot.test",
        status="published",
    ),
    EventSeed(
        name="Russian Nationals Finals",
        start_offset_days=-5,
        duration_days=2,
        city="Sochi",
        level="national",
        participants_count=54,
        style="park",
        has_best_trick=True,
        source_url="https://topscoot.test/events/rus-nationals",
        organizer_contact="nationals@topscoot.test",
        status="published",
    ),
    EventSeed(
        name="Siberian Street Clash",
        start_offset_days=-15,
        duration_days=1,
        city="Novosibirsk",
        level="regional",
        participants_count=28,
        style="street",
        has_best_trick=False,
        source_url="https://topscoot.test/events/siberian-clash",
        organizer_contact="siberia@topscoot.test",
        status="draft",
    ),
    EventSeed(
        name="Sochi Rookie Battle",
        start_offset_days=-120,
        duration_days=1,
        city="Sochi",
        level="local",
        participants_count=30,
        style="park",
        has_best_trick=False,
        source_url="https://topscoot.test/events/sochi-rookie",
        organizer_contact="rookie@topscoot.test",
        status="published",
    ),
]


def insert_event(conn: sqlite3.Connection, seed: EventSeed) -> bool:
    start_date = date.today() + timedelta(days=seed.start_offset_days)
    end_date = start_date + timedelta(days=max(seed.duration_days - 1, 0))
    date_start = start_date.strftime("%Y-%m-%d")
    date_end = end_date.strftime("%Y-%m-%d") if seed.duration_days > 1 else None

    cur = conn.execute(
        "SELECT id FROM events WHERE name = ? AND date_start = ?",
        (seed.name, date_start),
    )
    if cur.fetchone():
        return False

    conn.execute(
        """
        INSERT INTO events (
            name, date_start, date_end, city, level, participants_count,
            style, has_best_trick, source_url, organizer_contact, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            seed.name,
            date_start,
            date_end,
            seed.city,
            seed.level,
            seed.participants_count,
            seed.style,
            int(seed.has_best_trick),
            seed.source_url,
            seed.organizer_contact,
            seed.status,
        ),
    )
    return True


def seed_events(db_path: Path) -> int:
    inserted = 0
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")
        for seed in SEEDS:
            if insert_event(conn, seed):
                inserted += 1
        conn.commit()
    return inserted


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    inserted = seed_events(DB_PATH)
    print(f"Inserted {inserted} events into {DB_PATH}")


if __name__ == "__main__":
    main()
