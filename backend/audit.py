"""Audit logging helpers."""

from __future__ import annotations

import json
from typing import Any

from flask import g

from backend.db import get_db


def record_audit(entity: str, entity_id: int | None, action: str, payload: dict[str, Any] | None = None) -> None:
    """Insert an audit log entry for the current user."""
    user = getattr(g, "current_user", None)
    user_id = user.get("id") if isinstance(user, dict) else None
    db = get_db()
    db.execute(
        """
        INSERT INTO audit_log (user_id, entity, entity_id, action, payload_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, entity, entity_id, action, json.dumps(payload or {})),
    )
    # The caller is expected to commit within the same request/transaction.
