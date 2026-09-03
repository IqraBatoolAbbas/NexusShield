"""Threat analytics endpoint."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from typing import Any

from fastapi import APIRouter, Depends

from ..database import db
from ..security import current_user

router = APIRouter()


@router.get("/api/analytics")
def analytics(user: sqlite3.Row = Depends(current_user)) -> dict[str, Any]:
    with closing(db()) as connection:
        total = connection.execute("SELECT COUNT(*) FROM events WHERE user_id=?", (user["id"],)).fetchone()[0]
        blocked = connection.execute(
            "SELECT COUNT(*) FROM events WHERE user_id=? AND decision IN ('blocked','honeypot')",
            (user["id"],),
        ).fetchone()[0]
        remediated = connection.execute(
            "SELECT COUNT(*) FROM events WHERE user_id=? AND feedback='false_positive'", (user["id"],)
        ).fetchone()[0]
        honeypots = connection.execute(
            "SELECT COUNT(*) FROM honeypots WHERE user_id=? AND status='ACTIVE'", (user["id"],)
        ).fetchone()[0]
        latency = connection.execute(
            "SELECT COALESCE(AVG(latency_ms), 0) FROM events WHERE user_id=?", (user["id"],)
        ).fetchone()[0]
        threats = {
            row["signature"]: row["count"]
            for row in connection.execute(
                "SELECT signature,COUNT(*) count FROM events WHERE user_id=? GROUP BY signature",
                (user["id"],),
            )
        }
    return {
        "scanned": total,
        "blocked": blocked,
        "remediated": remediated,
        "honeypots": honeypots,
        "latency_ms": round(float(latency), 2),
        "threats": threats,
        "layers": {"Layer 1": total, "Layer 2": total, "Layer 4": blocked, "Layer 5": 0},
    }
