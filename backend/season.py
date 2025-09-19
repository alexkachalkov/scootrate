"""Season-related helpers (rolling points calculation)."""

from __future__ import annotations

from datetime import date, timedelta
import mysql.connector


def recalculate_season_points(
    conn: mysql.connector.connection.MySQLConnection,
    window_days: int = 90,
    points_cap: int = 1000,
) -> None:
    """Recompute rolling season points for all riders.

    Deletes existing cache and fills it with sums for events in the last
    ``window_days`` days, applying the ``points_cap`` limit per rider.
    """

    cutoff = (date.today() - timedelta(days=window_days)).strftime("%Y-%m-%d")

    cursor = conn.cursor()
    cursor.execute("DELETE FROM season_points")
    
    cursor.execute(
        """
        SELECT r.rider_id, COALESCE(SUM(r.points), 0) AS total_points
        FROM results AS r
        JOIN events AS e ON e.id = r.event_id
        WHERE date(e.date_start) >= %s
        GROUP BY r.rider_id
        """,
        (cutoff,),
    )

    for rider_id, total_points in cursor.fetchall():
        capped = min(int(total_points), points_cap)
        cursor.execute(
            """
            INSERT INTO season_points (rider_id, season_points, season_updated_at)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                season_points = VALUES(season_points),
                season_updated_at = VALUES(season_updated_at)
            """,
            (rider_id, capped),
        )
    cursor.close()
