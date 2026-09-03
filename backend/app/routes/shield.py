"""Firewall, policy, audit, API-key, and ingestion endpoints."""

from __future__ import annotations

import hashlib
import secrets
import sqlite3
import uuid
from contextlib import closing
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from ..core_engine import execute_scan
from ..database import db, get_policy, now
from ..models import FeedbackRequest, KeyRequest, PolicyUpdate, RoleUpdate, ScanRequest
from ..security import current_user, require_role, resolve_api_user

router = APIRouter()


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "nexusshield", "storage": "sqlite", "encryption": "AES-256-CBC"}


@router.get("/api/policy")
def policy(user: sqlite3.Row = Depends(current_user)) -> dict[str, Any]:
    return get_policy(user["id"])


@router.put("/api/policy")
def update_policy(
    update: PolicyUpdate, user: sqlite3.Row = Depends(require_role("admin", "developer"))
) -> dict[str, Any]:
    with closing(db()) as connection:
        connection.execute(
            "UPDATE policy SET similarity_threshold=?, enable_honeypot=?, strict_pii=?, strict_toxicity=?, auto_block_dos=?, updated_at=? WHERE user_id=?",
            (
                update.similarity_threshold,
                update.enable_honeypot,
                update.strict_pii,
                update.strict_toxicity,
                update.auto_block_dos,
                now(),
                user["id"],
            ),
        )
        connection.commit()
    return get_policy(user["id"])


@router.get("/api/keys")
def list_keys(user: sqlite3.Row = Depends(require_role("admin", "developer"))) -> list[dict[str, Any]]:
    with closing(db()) as connection:
        rows = connection.execute(
            "SELECT id,name,prefix,created_at,revoked_at FROM api_keys WHERE user_id=? ORDER BY created_at DESC",
            (user["id"],),
        ).fetchall()
    return [dict(row) for row in rows]


@router.post("/api/keys")
def create_key(
    request: KeyRequest, user: sqlite3.Row = Depends(require_role("admin", "developer"))
) -> dict[str, Any]:
    raw_key = f"ns_live_sec_{secrets.token_urlsafe(32)}"
    key_id = f"key_{uuid.uuid4().hex[:12]}"
    with closing(db()) as connection:
        connection.execute(
            "INSERT INTO api_keys VALUES (?,?,?,?,?,?,?)",
            (key_id, user["id"], request.name, hashlib.sha256(raw_key.encode()).hexdigest(), raw_key[:18], now(), None),
        )
        connection.commit()
    return {"id": key_id, "name": request.name, "key": raw_key, "prefix": raw_key[:18]}


@router.delete("/api/keys/{key_id}")
def revoke_key(
    key_id: str, user: sqlite3.Row = Depends(require_role("admin", "developer"))
) -> dict[str, str]:
    with closing(db()) as connection:
        cursor = connection.execute(
            "UPDATE api_keys SET revoked_at=? WHERE id=? AND user_id=? AND revoked_at IS NULL",
            (now(), key_id, user["id"]),
        )
        connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="API key not found")
    return {"status": "revoked"}


@router.get("/api/events")
def list_events(limit: int = 50, user: sqlite3.Row = Depends(current_user)) -> list[dict[str, Any]]:
    with closing(db()) as connection:
        rows = connection.execute(
            "SELECT id,prompt,decision,signature,similarity,client_id,session_id,latency_ms,feedback,previous_hash,chain_hash,created_at FROM events WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user["id"], max(1, min(limit, 200))),
        ).fetchall()
    return [dict(row) for row in rows]


@router.get("/api/honeypots")
def list_honeypots(user: sqlite3.Row = Depends(current_user)) -> list[dict[str, Any]]:
    with closing(db()) as connection:
        rows = connection.execute(
            "SELECT * FROM honeypots WHERE user_id=? ORDER BY updated_at DESC", (user["id"],)
        ).fetchall()
    return [dict(row) for row in rows]


@router.post("/api/audit/verify")
def verify_audit(user: sqlite3.Row = Depends(require_role("admin", "auditor"))) -> dict[str, Any]:
    with closing(db()) as connection:
        rows = connection.execute(
            "SELECT id,user_id,encrypted_trace,previous_hash,chain_hash FROM events WHERE user_id=? ORDER BY created_at ASC",
            (user["id"],),
        ).fetchall()
    previous = ""
    valid = True
    for row in rows:
        expected = hashlib.sha256(
            f"{row['id']}|{row['user_id']}|{row['encrypted_trace']}|{previous}".encode()
        ).hexdigest()
        valid = valid and row["previous_hash"] == previous and row["chain_hash"] == expected
        previous = row["chain_hash"]
    return {
        "valid": valid,
        "events_checked": len(rows),
        "algorithm": "SHA-256 chain over AES-256-CBC payloads",
    }


@router.post("/api/feedback")
def feedback(
    request: FeedbackRequest, user: sqlite3.Row = Depends(current_user)
) -> dict[str, Any]:
    with closing(db()) as connection:
        event = connection.execute(
            "SELECT similarity FROM events WHERE id=? AND user_id=?", (request.event_id, user["id"])
        ).fetchone()
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        connection.execute(
            "UPDATE events SET feedback=? WHERE id=? AND user_id=?",
            (request.verdict, request.event_id, user["id"]),
        )
        if request.verdict in {"false_positive", "confirmed_attack"}:
            delta = 0.01 if request.verdict == "false_positive" else -0.01
            connection.execute(
                "UPDATE policy SET similarity_threshold=MIN(.99,MAX(.50,similarity_threshold+?)),updated_at=? WHERE user_id=?",
                (delta, now(), user["id"]),
            )
        connection.commit()
    return {"status": "recorded", "new_policy": get_policy(user["id"])}


@router.patch("/api/team/{member_id}/role")
def update_member_role(
    member_id: str,
    update: RoleUpdate,
    user: sqlite3.Row = Depends(require_role("admin")),
) -> dict[str, str]:
    with closing(db()) as connection:
        cursor = connection.execute(
            "UPDATE users SET role=? WHERE id=? AND tenant_id=?",
            (update.role, member_id, user["tenant_id"]),
        )
        connection.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Team member not found")
    return {"status": "updated", "role": update.role}


@router.get("/api/billing")
def billing(user: sqlite3.Row = Depends(require_role("admin"))) -> dict[str, Any]:
    with closing(db()) as connection:
        scans = connection.execute("SELECT COUNT(*) FROM events WHERE user_id=?", (user["id"],)).fetchone()[0]
    return {"plan": "Developer Free", "monthly_quota": 10000, "used": scans, "renewal": "Monthly", "status": "active"}


@router.post("/api/scan")
def scan(
    request: ScanRequest,
    http_request: Request,
    user: sqlite3.Row = Depends(current_user),
) -> dict[str, Any]:
    return execute_scan(request, http_request, user)


@router.post("/api/events/{event_id}/replay")
def replay(
    event_id: str,
    http_request: Request,
    user: sqlite3.Row = Depends(current_user),
) -> dict[str, Any]:
    """Replay a tenant-owned event through the current policy and pipeline."""
    with closing(db()) as connection:
        event = connection.execute(
            "SELECT prompt, session_id, client_id FROM events WHERE id=? AND user_id=?",
            (event_id, user["id"]),
        ).fetchone()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    replay_request = ScanRequest(
        prompt=event["prompt"],
        session_id=f"replay:{event['session_id']}",
        client_id=event["client_id"],
    )
    result = execute_scan(replay_request, http_request, user)
    result["replay_of"] = event_id
    return result


@router.post("/api/ingest")
def ingest(
    request: ScanRequest,
    http_request: Request,
    x_api_key: str | None = Header(default=None),
) -> dict[str, Any]:
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-Key header required")
    return execute_scan(request, http_request, resolve_api_user(x_api_key))
