"""Season-related helpers (rolling points calculation)."""

from __future__ import annotations

from datetime import date, timedelta
import sqlite3


def recalculate_season_points(
    conn: sqlite3.Connection,
    window_days: int = 90,
    points_cap: int = 1000,
) -> None:
    """Recompute rolling season points for all riders.

    Deletes existing cache and fills it with sums for events in the last
    ``window_days`` days, applying the ``points_cap`` limit per rider.
    """

    cutoff = (date.today() - timedelta(days=window_days)).strftime("%Y-%m-%d")

    conn.execute("DELETE FROM season_points")
    cur = conn.execute(
        """
        SELECT r.rider_id, COALESCE(SUM(r.points), 0) AS total_points
        FROM results AS r
        JOIN events AS e ON e.id = r.event_id
        WHERE date(e.date_start) >= date(?)
        GROUP BY r.rider_id
        """,
        (cutoff,),
    )

    for rider_id, total_points in cur.fetchall():
        capped = min(int(total_points), points_cap)
        conn.execute(
            """
            INSERT OR REPLACE INTO season_points (rider_id, season_points, season_updated_at)
            VALUES (?, ?, datetime('now'))
            """,
            (rider_id, capped),
        )
