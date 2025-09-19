"""Authentication helpers for admin routes."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

import bcrypt
from flask import Response, current_app, g, jsonify, session

from backend.db import get_db

F = TypeVar("F", bound=Callable[..., Response | tuple[Any, int] | tuple[Any, int, dict[str, Any]]])

SESSION_USER_KEY = "admin_user"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def get_current_user() -> dict[str, Any] | None:
    return session.get(SESSION_USER_KEY)


def set_current_user(user: dict[str, Any]) -> None:
    session[SESSION_USER_KEY] = {
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
    }


def clear_current_user() -> None:
    session.pop(SESSION_USER_KEY, None)


def login_required(role: str | None = None) -> Callable[[F], F]:
    def decorator(view: F) -> F:
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any):  # type: ignore[misc]
            user = get_current_user()
            if not user:
                return jsonify({"error": "Unauthorized"}), 401
            if role and user.get("role") != role and user.get("role") != "admin":
                return jsonify({"error": "Forbidden"}), 403
            g.current_user = user
            return view(*args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorator


def fetch_user_by_email(email: str) -> dict[str, Any] | None:
    db = get_db()
    row = db.execute(
        "SELECT id, email, password_hash, role FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    if row:
        return dict(row)
    return None


def touch_last_login(user_id: int) -> None:
    db = get_db()
    db.execute(
        "UPDATE users SET last_login_at = datetime('now') WHERE id = ?",
        (user_id,),
    )
    db.commit()
