"""Authentication, authorization, API keys, and encrypted audit payloads."""

from __future__ import annotations

import base64
import hashlib
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from typing import Callable

import jwt
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi import Depends, Header, HTTPException, status

from .database import db

JWT_SECRET = os.getenv("NEXUSSHIELD_JWT_SECRET", "replace-this-secret-in-production")


def token_for(user: sqlite3.Row) -> str:
    return jwt.encode(
        {
            "sub": user["id"],
            "email": user["email"],
            "exp": datetime.now(timezone.utc) + timedelta(hours=12),
        },
        JWT_SECRET,
        algorithm="HS256",
    )


def current_user(authorization: str | None = Header(default=None)) -> sqlite3.Row:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="****** required")
    try:
        payload = jwt.decode(authorization[7:], JWT_SECRET, algorithms=["HS256"])
        user_id = payload["sub"]
    except (jwt.InvalidTokenError, KeyError) as error:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from error
    with closing(db()) as connection:
        user = connection.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


def require_role(*roles: str) -> Callable:
    def dependency(user: sqlite3.Row = Depends(current_user)) -> sqlite3.Row:
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Your role is not authorized for this resource")
        return user

    return dependency


def encrypt_log(payload: str) -> str:
    password = os.getenv("NEXUSSHIELD_LOG_KEY", "change-this-local-demo-key").encode()
    salt = hashlib.sha256(b"nexusshield-salt").digest()[:16]
    key = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=120_000
    ).derive(password)
    iv = os.urandom(16)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(payload.encode()) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return base64.b64encode(iv + encryptor.update(padded) + encryptor.finalize()).decode()


def resolve_api_user(api_key: str) -> sqlite3.Row:
    with closing(db()) as connection:
        row = connection.execute(
            "SELECT user_id FROM api_keys WHERE key_hash=? AND revoked_at IS NULL",
            (hashlib.sha256(api_key.encode()).hexdigest(),),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=401, detail="Invalid or revoked API key")
        user = connection.execute("SELECT * FROM users WHERE id=?", (row["user_id"],)).fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="API key owner not found")
    return user
