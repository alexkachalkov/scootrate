"""Public API endpoints."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from flask import Blueprint, jsonify, request

from backend.db import get_db

bp = Blueprint("public", __name__, url_prefix="/api")


@bp.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"})


def parse_int(value: str | None, default: int | None = None) -> int | None:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@bp.get("/rating")
def get_rating() -> Any:
    db = get_db()
    city = request.args.get("city")
    level = request.args.get("level")
    style = request.args.get("style")
    search = request.args.get("search")
    age_min = parse_int(request.args.get("ageMin"))
    age_max = parse_int(request.args.get("ageMax"))
    all_ages = request.args.get("allAges") == "1"
    page = max(parse_int(request.args.get("page"), 1) or 1, 1)
    limit = parse_int(request.args.get("limit"), 50) or 50

    where_clauses: list[str] = []
    params: list[Any] = []

    if city:
        where_clauses.append("r.city LIKE ?")
        params.append(f"%{city}%")
    if level:
        where_clauses.append("r.level = ?")
        params.append(level)
    if style:
        where_clauses.append("r.style = ?")
        params.append(style)
    if search:
        where_clauses.append("(lower(r.nickname) LIKE lower(?) OR lower(COALESCE(r.fullname, '')) LIKE lower(?))")
        params.extend([f"%{search}%", f"%{search}%"])
    if not all_ages:
        today = date.today()
        if age_min is not None:
            max_birth = subtract_years(today, age_min)
            where_clauses.append("date(r.birthdate) <= date(?)")
            params.append(max_birth.isoformat())
        if age_max is not None:
            min_birth = subtract_years(today, age_max + 1) + timedelta(days=1)
            where_clauses.append("date(r.birthdate) >= date(?)")
            params.append(min_birth.isoformat())

    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = "WHERE " + where_sql

    count_sql = f"""
        SELECT COUNT(*)
        FROM riders AS r
        LEFT JOIN season_points AS sp ON sp.rider_id = r.id
        {where_sql}
    """
    total = db.execute(count_sql, params).fetchone()[0]

    offset = (page - 1) * limit
    query_sql = f"""
        SELECT r.id, r.nickname, r.fullname, r.city, r.birthdate, r.style, r.level,
               COALESCE(sp.season_points, 0) AS season_points
        FROM riders AS r
        LEFT JOIN season_points AS sp ON sp.rider_id = r.id
        {where_sql}
        ORDER BY season_points DESC, r.id ASC
        LIMIT ? OFFSET ?
    """
    rows = db.execute(query_sql, (*params, limit, offset)).fetchall()

    items = []
    for row in rows:
        age = calculate_age(row["birthdate"])
        items.append(
            {
                "id": row["id"],
                "nickname": row["nickname"],
                "fullname": row["fullname"],
                "city": row["city"],
                "birthdate": row["birthdate"],
                "age": age,
                "style": row["style"],
                "level": row["level"],
                "seasonPoints": row["season_points"],
            }
        )

    return jsonify({"items": items, "total": total, "page": page, "limit": limit})


def calculate_age(birthdate: str | None) -> int | None:
    if not birthdate:
        return None
    try:
        year, month, day = map(int, birthdate.split("-"))
        born = date(year, month, day)
    except ValueError:
        return None

    today = date.today()
    age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    return age


def subtract_years(dt: date, years: int) -> date:
    try:
        return dt.replace(year=dt.year - years)
    except ValueError:
        # Handle February 29 for non-leap years
        return dt.replace(month=2, day=28, year=dt.year - years)


@bp.get("/riders/<int:rider_id>")
def get_rider(rider_id: int) -> Any:
    db = get_db()
    rider = db.execute(
        """
        SELECT r.*, COALESCE(sp.season_points, 0) AS season_points
        FROM riders AS r
        LEFT JOIN season_points AS sp ON sp.rider_id = r.id
        WHERE r.id = ?
        """,
        (rider_id,),
    ).fetchone()
    if not rider:
        return jsonify({"error": "Not found"}), 404

    results = db.execute(
        """
        SELECT e.id AS event_id, e.name, e.city, e.level, e.date_start,
               res.place, res.is_finalist, res.is_participant, res.points
        FROM results AS res
        JOIN events AS e ON e.id = res.event_id
        WHERE res.rider_id = ?
        ORDER BY e.date_start DESC
        LIMIT 50
        """,
        (rider_id,),
    ).fetchall()

    return jsonify(
        {
            "rider": {
                "id": rider["id"],
                "nickname": rider["nickname"],
                "fullname": rider["fullname"],
                "city": rider["city"],
                "birthdate": rider["birthdate"],
                "age": calculate_age(rider["birthdate"]),
                "style": rider["style"],
                "level": rider["level"],
                "seasonPoints": rider["season_points"],
            },
            "seasonResults": [
                {
                    "eventId": row["event_id"],
                    "eventName": row["name"],
                    "eventCity": row["city"],
                    "eventLevel": row["level"],
                    "eventDate": row["date_start"],
                    "place": row["place"],
                    "isFinalist": bool(row["is_finalist"]),
                    "isParticipant": bool(row["is_participant"]),
                    "points": row["points"],
                }
                for row in results
            ],
        }
    )


@bp.get("/events")
def get_events() -> Any:
    db = get_db()
    city = request.args.get("city")
    level = request.args.get("level")

    where_clauses: list[str] = ["e.status = 'published'"]
    params: list[Any] = []
    if city:
        where_clauses.append("e.city LIKE ?")
        params.append(f"%{city}%")
    if level:
        where_clauses.append("e.level = ?")
        params.append(level)

    where_sql = " AND ".join(where_clauses)
    if where_sql:
        where_sql = "WHERE " + where_sql

    rows = db.execute(
        f"""
        SELECT e.id, e.name, e.date_start, e.date_end, e.city, e.level,
               e.participants_count, e.style
        FROM events AS e
        {where_sql}
        ORDER BY e.date_start DESC
        LIMIT 50
        """,
        params,
    ).fetchall()

    return jsonify(
        {
            "items": [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "dateStart": row["date_start"],
                    "dateEnd": row["date_end"],
                    "city": row["city"],
                    "level": row["level"],
                    "participants": row["participants_count"],
                    "style": row["style"],
                }
                for row in rows
            ]
        }
    )


@bp.get("/events/<int:event_id>")
def get_event(event_id: int) -> Any:
    db = get_db()
    event = db.execute(
        """
        SELECT * FROM events WHERE id = ?
        """,
        (event_id,),
    ).fetchone()
    if not event:
        return jsonify({"error": "Not found"}), 404

    results = db.execute(
        """
        SELECT r.id AS rider_id, r.nickname, r.city, r.level,
               res.place, res.is_finalist, res.is_participant, res.points
        FROM results AS res
        JOIN riders AS r ON r.id = res.rider_id
        WHERE res.event_id = ?
        ORDER BY res.place IS NULL, res.place ASC
        """,
        (event_id,),
    ).fetchall()

    return jsonify(
        {
            "event": {
                "id": event["id"],
                "name": event["name"],
                "dateStart": event["date_start"],
                "dateEnd": event["date_end"],
                "city": event["city"],
                "level": event["level"],
                "participants": event["participants_count"],
                "style": event["style"],
                "hasBestTrick": bool(event["has_best_trick"]),
                "sourceUrl": event["source_url"],
                "organizerContact": event["organizer_contact"],
                "status": event["status"],
            },
            "results": [
                {
                    "riderId": row["rider_id"],
                    "nickname": row["nickname"],
                    "city": row["city"],
                    "riderLevel": row["level"],
                    "place": row["place"],
                    "isFinalist": bool(row["is_finalist"]),
                    "isParticipant": bool(row["is_participant"]),
                    "points": row["points"],
                }
                for row in results
            ],
        }
    )
