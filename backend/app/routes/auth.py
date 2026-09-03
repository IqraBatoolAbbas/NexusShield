"""Authentication and account-management endpoints."""

from __future__ import annotations

import sqlite3
import uuid
from contextlib import closing
from typing import Any

import bcrypt
from fastapi import APIRouter, Depends, HTTPException

from ..database import db, now
from ..models import Credentials
from ..security import current_user, require_role, token_for

router = APIRouter()


@router.post("/api/auth/signup")
def signup(credentials: Credentials) -> dict[str, Any]:
    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    with closing(db()) as connection:
        try:
            connection.execute(
                "INSERT INTO users (id,tenant_id,email,name,password_hash,role,created_at) VALUES (?,?,?,?,?,?,?)",
                (
                    user_id,
                    user_id,
                    credentials.email.lower(),
                    credentials.name,
                    bcrypt.hashpw(credentials.password.encode(), bcrypt.gensalt()).decode(),
                    credentials.role,
                    now(),
                ),
            )
            connection.execute("INSERT INTO policy (user_id, updated_at) VALUES (?,?)", (user_id, now()))
            connection.commit()
        except sqlite3.IntegrityError as error:
            raise HTTPException(status_code=409, detail="An account with this email already exists") from error
        user = connection.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return {
        "access_token": token_for(user),
        "token_type": "bearer",
        "user": {"id": user_id, "email": user["email"], "name": user["name"], "role": user["role"]},
    }


@router.post("/api/auth/login")
def login(credentials: Credentials) -> dict[str, Any]:
    with closing(db()) as connection:
        user = connection.execute("SELECT * FROM users WHERE email=?", (credentials.email.lower(),)).fetchone()
    if user is None or not bcrypt.checkpw(credentials.password.encode(), user["password_hash"].encode()):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "access_token": token_for(user),
        "token_type": "bearer",
        "user": {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]},
    }


@router.get("/api/me")
def me(user: sqlite3.Row = Depends(current_user)) -> dict[str, Any]:
    return {"id": user["id"], "email": user["email"], "name": user["name"], "role": user["role"]}


@router.get("/api/team")
def team(user: sqlite3.Row = Depends(require_role("admin"))) -> list[dict[str, Any]]:
    with closing(db()) as connection:
        return [
            dict(row)
            for row in connection.execute(
                "SELECT id,email,name,role,created_at FROM users WHERE tenant_id=?",
                (user["tenant_id"],),
            )
        ]
