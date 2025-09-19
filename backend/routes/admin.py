"""Admin authentication endpoints."""

from __future__ import annotations

import time
from typing import Any

from flask import Blueprint, jsonify, request, g

from backend.auth import (
    clear_current_user,
    fetch_user_by_email,
    get_current_user,
    login_required,
    set_current_user,
    touch_last_login,
    verify_password,
)
from backend.db import get_db
from backend.season import recalculate_season_points
from backend.audit import record_audit

bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# naive in-memory rate limiter for login attempts
_LOGIN_ATTEMPTS: dict[str, list[float]] = {}
_LOGIN_WINDOW = 300  # seconds
_MAX_ATTEMPTS = 10


def is_rate_limited(identifier: str) -> bool:
    now = time.time()
    attempts = _LOGIN_ATTEMPTS.setdefault(identifier, [])
    # remove expired attempts
    _LOGIN_ATTEMPTS[identifier] = [ts for ts in attempts if now - ts <= _LOGIN_WINDOW]
    return len(_LOGIN_ATTEMPTS[identifier]) >= _MAX_ATTEMPTS


def register_attempt(identifier: str) -> None:
    now = time.time()
    attempts = _LOGIN_ATTEMPTS.setdefault(identifier, [])
    attempts.append(now)
    _LOGIN_ATTEMPTS[identifier] = [ts for ts in attempts if now - ts <= _LOGIN_WINDOW]


@bp.post("/login")
def login() -> Any:
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    identifier = request.remote_addr or email
    if is_rate_limited(identifier):
        return jsonify({"error": "Too many attempts"}), 429

    if not email or not password:
        register_attempt(identifier)
        return jsonify({"error": "Invalid credentials"}), 400

    user = fetch_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        register_attempt(identifier)
        return jsonify({"error": "Invalid credentials"}), 401

    clear_current_user()
    set_current_user(user)
    touch_last_login(user["id"])
    return jsonify({"message": "Logged in", "user": {"email": user["email"], "role": user["role"]}})


@bp.post("/logout")
@login_required()
def logout() -> Any:
    clear_current_user()
    return jsonify({"message": "Logged out"})


@bp.get("/me")
@login_required()
def me() -> Any:
    user = get_current_user()
    return jsonify({"user": user})


# Riders management ---------------------------------------------------------


REQUIRED_RIDER_FIELDS = [
    "nickname",
    "city",
    "birthdate",
    "style",
    "level",
]


def validate_rider_payload(data: dict[str, Any], partial: bool = False) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for field in REQUIRED_RIDER_FIELDS:
        if not partial and not data.get(field):
            errors.append(f"Field {field} is required")
    return (len(errors) == 0, errors)


def serialize_rider(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "nickname": row["nickname"],
        "fullname": row["fullname"],
        "city": row["city"],
        "birthdate": row["birthdate"],
        "style": row["style"],
        "level": row["level"],
        "photoUrl": row["photo_url"],
        "email": row["email"],
        "socialsJson": row["socials_json"],
    }


@bp.get("/riders")
@login_required("editor")
def admin_list_riders() -> Any:
    db = get_db()
    search = request.args.get("search")
    level = request.args.get("level")
    style = request.args.get("style")
    city = request.args.get("city")
    page = max(request.args.get("page", type=int) or 1, 1)
    limit = min(max(request.args.get("limit", type=int) or 50, 1), 200)

    where: list[str] = []
    params: list[Any] = []

    if search:
        like = f"%{search}%"
        where.append("(lower(nickname) LIKE lower(?) OR lower(COALESCE(fullname,'')) LIKE lower(?))")
        params.extend([like, like])
    if level:
        where.append("level = ?")
        params.append(level)
    if style:
        where.append("style = ?")
        params.append(style)
    if city:
        where.append("lower(city) LIKE lower(?)")
        params.append(f"%{city}%")

    where_sql = " AND ".join(where)
    if where_sql:
        where_sql = "WHERE " + where_sql

    total = db.execute(
        f"SELECT COUNT(*) FROM riders {where_sql}",
        params,
    ).fetchone()[0]

    offset = (page - 1) * limit
    rows = db.execute(
        f"SELECT * FROM riders {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (*params, limit, offset),
    ).fetchall()

    return jsonify({
        "items": [serialize_rider(row) for row in rows],
        "total": total,
        "page": page,
        "limit": limit,
    })


@bp.post("/riders")
@login_required("editor")
def admin_create_rider() -> Any:
    data = request.get_json(silent=True) or {}
    valid, errors = validate_rider_payload(data)
    if not valid:
        return jsonify({"errors": errors}), 400

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO riders (nickname, fullname, city, birthdate, style, level, photo_url, email, socials_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("nickname"),
            data.get("fullname"),
            data.get("city"),
            data.get("birthdate"),
            data.get("style"),
            data.get("level"),
            data.get("photoUrl"),
            data.get("email"),
            data.get("socialsJson") or "{}",
        ),
    )
    rider_id = cursor.lastrowid
    row = db.execute("SELECT * FROM riders WHERE id = ?", (rider_id,)).fetchone()
    record_audit("rider", rider_id, "create", {"nickname": data.get("nickname"), "city": data.get("city")})
    db.commit()
    return jsonify({"rider": serialize_rider(row)}), 201


@bp.put("/riders/<int:rider_id>")
@login_required("editor")
def admin_update_rider(rider_id: int) -> Any:
    data = request.get_json(silent=True) or {}
    valid, errors = validate_rider_payload(data, partial=True)
    if not valid:
        return jsonify({"errors": errors}), 400

    db = get_db()
    existing = db.execute("SELECT * FROM riders WHERE id = ?", (rider_id,)).fetchone()
    if not existing:
        return jsonify({"error": "Not found"}), 404

    db.execute(
        """
        UPDATE riders
        SET nickname = COALESCE(?, nickname),
            fullname = COALESCE(?, fullname),
            city = COALESCE(?, city),
            birthdate = COALESCE(?, birthdate),
            style = COALESCE(?, style),
            level = COALESCE(?, level),
            photo_url = COALESCE(?, photo_url),
            email = COALESCE(?, email),
            socials_json = COALESCE(?, socials_json),
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (
            data.get("nickname"),
            data.get("fullname"),
            data.get("city"),
            data.get("birthdate"),
            data.get("style"),
            data.get("level"),
            data.get("photoUrl"),
            data.get("email"),
            data.get("socialsJson"),
            rider_id,
        ),
    )
    row = db.execute("SELECT * FROM riders WHERE id = ?", (rider_id,)).fetchone()
    record_audit("rider", rider_id, "update", {key: data.get(key) for key in data.keys()})
    db.commit()
    return jsonify({"rider": serialize_rider(row)})


@bp.delete("/riders/<int:rider_id>")
@login_required("editor")
def admin_delete_rider(rider_id: int) -> Any:
    db = get_db()
    cursor = db.execute("DELETE FROM riders WHERE id = ?", (rider_id,))
    if cursor.rowcount == 0:
        return jsonify({"error": "Not found"}), 404
    record_audit("rider", rider_id, "delete", {})
    db.commit()
    return jsonify({"message": "Deleted"})


# Events management ---------------------------------------------------------


REQUIRED_EVENT_FIELDS = [
    "name",
    "date_start",
    "city",
    "level",
]


def validate_event_payload(data: dict[str, Any], partial: bool = False) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for field in REQUIRED_EVENT_FIELDS:
        if not partial and not data.get(field):
            errors.append(f"Field {field} is required")
    level = data.get("level")
    if level and level not in {"local", "regional", "national", "international"}:
        errors.append("Invalid level")
    status = data.get("status")
    if status and status not in {"draft", "published"}:
        errors.append("Invalid status")
    return (len(errors) == 0, errors)


def serialize_event(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "dateStart": row["date_start"],
        "dateEnd": row["date_end"],
        "city": row["city"],
        "level": row["level"],
        "participantsCount": row["participants_count"],
        "style": row["style"],
        "hasBestTrick": bool(row["has_best_trick"]),
        "sourceUrl": row["source_url"],
        "organizerContact": row["organizer_contact"],
        "status": row["status"],
    }


@bp.get("/events")
@login_required("editor")
def admin_list_events() -> Any:
    db = get_db()
    status = request.args.get("status")
    level = request.args.get("level")
    city = request.args.get("city")
    search = request.args.get("search")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    page = max(request.args.get("page", type=int) or 1, 1)
    limit = min(max(request.args.get("limit", type=int) or 50, 1), 200)

    where: list[str] = []
    params: list[Any] = []
    if status:
        where.append("status = ?")
        params.append(status)
    if level:
        where.append("level = ?")
        params.append(level)
    if city:
        where.append("lower(city) LIKE lower(?)")
        params.append(f"%{city}%")
    if search:
        where.append("lower(name) LIKE lower(?)")
        params.append(f"%{search}%")
    if date_from:
        where.append("date(date_start) >= date(?)")
        params.append(date_from)
    if date_to:
        where.append("date(date_start) <= date(?)")
        params.append(date_to)

    where_sql = " AND ".join(where)
    if where_sql:
        where_sql = "WHERE " + where_sql

    total = db.execute(
        f"SELECT COUNT(*) FROM events {where_sql}",
        params,
    ).fetchone()[0]

    offset = (page - 1) * limit
    rows = db.execute(
        f"SELECT * FROM events {where_sql} ORDER BY date_start DESC LIMIT ? OFFSET ?",
        (*params, limit, offset),
    ).fetchall()

    return jsonify({
        "items": [serialize_event(row) for row in rows],
        "total": total,
        "page": page,
        "limit": limit,
    })


@bp.post("/events")
@login_required("editor")
def admin_create_event() -> Any:
    data = request.get_json(silent=True) or {}
    valid, errors = validate_event_payload(data)
    if not valid:
        return jsonify({"errors": errors}), 400

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO events (
            name, date_start, date_end, city, level, participants_count,
            style, has_best_trick, source_url, organizer_contact, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("name"),
            data.get("date_start"),
            data.get("date_end"),
            data.get("city"),
            data.get("level"),
            data.get("participants_count"),
            data.get("style"),
            int(bool(data.get("has_best_trick"))),
            data.get("source_url"),
            data.get("organizer_contact"),
            data.get("status") or "draft",
        ),
    )
    event_id = cursor.lastrowid
    row = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    recalculate_season_points(db)
    record_audit("event", event_id, "create", {"name": data.get("name"), "status": row["status"]})
    db.commit()
    return jsonify({"event": serialize_event(row)}), 201


@bp.put("/events/<int:event_id>")
@login_required("editor")
def admin_update_event(event_id: int) -> Any:
    data = request.get_json(silent=True) or {}
    valid, errors = validate_event_payload(data, partial=True)
    if not valid:
        return jsonify({"errors": errors}), 400

    db = get_db()
    existing = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if not existing:
        return jsonify({"error": "Not found"}), 404

    db.execute(
        """
        UPDATE events
        SET name = COALESCE(?, name),
            date_start = COALESCE(?, date_start),
            date_end = COALESCE(?, date_end),
            city = COALESCE(?, city),
            level = COALESCE(?, level),
            participants_count = COALESCE(?, participants_count),
            style = COALESCE(?, style),
            has_best_trick = COALESCE(?, has_best_trick),
            source_url = COALESCE(?, source_url),
            organizer_contact = COALESCE(?, organizer_contact),
            status = COALESCE(?, status),
            updated_at = datetime('now')
        WHERE id = ?
        """,
        (
            data.get("name"),
            data.get("date_start"),
            data.get("date_end"),
            data.get("city"),
            data.get("level"),
            data.get("participants_count"),
            data.get("style"),
            int(data.get("has_best_trick")) if data.get("has_best_trick") is not None else None,
            data.get("source_url"),
            data.get("organizer_contact"),
            data.get("status"),
            event_id,
        ),
    )
    row = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    if row["status"] == "published":
        recalculate_season_points(db)
    record_audit("event", event_id, "update", {key: data.get(key) for key in data.keys()})
    db.commit()
    return jsonify({"event": serialize_event(row)})


@bp.post("/events/<int:event_id>/publish")
@login_required("editor")
def admin_publish_event(event_id: int) -> Any:
    db = get_db()
    cursor = db.execute(
        "UPDATE events SET status = 'published', updated_at = datetime('now') WHERE id = ?",
        (event_id,),
    )
    if cursor.rowcount == 0:
        return jsonify({"error": "Not found"}), 404
    row = db.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    recalculate_season_points(db)
    record_audit("event", event_id, "publish", {})
    db.commit()
    return jsonify({"event": serialize_event(row)})


# Results management --------------------------------------------------------


def serialize_result(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "eventId": row["event_id"],
        "riderId": row["rider_id"],
        "place": row["place"],
        "isFinalist": bool(row["is_finalist"]),
        "isParticipant": bool(row["is_participant"]),
        "points": row["points"],
        "comment": row["comment"],
    }


@bp.get("/results")
@login_required("editor")
def admin_list_results() -> Any:
    event_id = request.args.get("eventId", type=int)
    if not event_id:
        return jsonify({"error": "eventId is required"}), 400
    db = get_db()
    rows = db.execute(
        "SELECT * FROM results WHERE event_id = ? ORDER BY place IS NULL, place ASC",
        (event_id,),
    ).fetchall()
    return jsonify({"items": [serialize_result(row) for row in rows]})


@bp.put("/results/<int:result_id>")
@login_required("editor")
def admin_update_result(result_id: int) -> Any:
    data = request.get_json(silent=True) or {}
    db = get_db()
    existing = db.execute("SELECT * FROM results WHERE id = ?", (result_id,)).fetchone()
    if not existing:
        return jsonify({"error": "Not found"}), 404

    if "points" in data and g.current_user.get("role") != "admin":
        return jsonify({"error": "Only admins can override points"}), 403

    db.execute(
        """
        UPDATE results
        SET place = COALESCE(?, place),
            is_finalist = COALESCE(?, is_finalist),
            is_participant = COALESCE(?, is_participant),
            points = COALESCE(?, points),
            comment = COALESCE(?, comment)
        WHERE id = ?
        """,
        (
            data.get("place"),
            int(data.get("isFinalist")) if data.get("isFinalist") is not None else None,
            int(data.get("isParticipant")) if data.get("isParticipant") is not None else None,
            data.get("points"),
            data.get("comment"),
            result_id,
        ),
    )
    row = db.execute("SELECT * FROM results WHERE id = ?", (result_id,)).fetchone()
    # recalc season points for rider
    record_audit("result", result_id, "update", {key: data.get(key) for key in data.keys()})
    recalculate_season_points(db)
    db.commit()
    return jsonify({"result": serialize_result(row)})


@bp.post("/recalculate-season")
@login_required("editor")
def admin_recalculate_season() -> Any:
    db = get_db()
    recalculate_season_points(db)
    record_audit("system", None, "recalculate_season", {})
    db.commit()
    return jsonify({"message": "Season points recalculated"})


@bp.post("/results/import-csv")
@login_required("editor")
def admin_import_results_csv() -> Any:
    # Placeholder implementation for MVP scaffolding
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    filename = file.filename or ""
    return jsonify({"message": "Import preview not implemented", "filename": filename}), 200
