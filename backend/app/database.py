"""SQLite configuration, connection helpers, and schema management."""

from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Vercel functions can only write to /tmp. This fallback keeps cold starts
# functional; persistent production deployments should provide a cloud DB.
default_data_dir = "/tmp/nexusshield" if os.getenv("VERCEL") else Path(__file__).resolve().parents[1] / "data"
DATA_DIR = Path(os.getenv("NEXUSSHIELD_DATA_DIR", default_data_dir))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "nexusshield.sqlite3"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def db() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create the current schema and migrate the old pre-tenant schema."""
    with closing(db()) as connection:
        for table in ("policy", "events", "honeypots"):
            existing = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
            if existing and "user_id" not in existing:
                connection.execute(f"ALTER TABLE {table} RENAME TO {table}_legacy")
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'admin',
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS policy (
                user_id TEXT PRIMARY KEY,
                similarity_threshold REAL NOT NULL DEFAULT .85,
                enable_honeypot INTEGER NOT NULL DEFAULT 1,
                strict_pii INTEGER NOT NULL DEFAULT 1,
                strict_toxicity INTEGER NOT NULL DEFAULT 1,
                auto_block_dos INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                prefix TEXT NOT NULL,
                created_at TEXT NOT NULL,
                revoked_at TEXT
            );
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                prompt TEXT NOT NULL,
                decision TEXT NOT NULL,
                signature TEXT NOT NULL,
                similarity REAL NOT NULL,
                client_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                feedback TEXT,
                encrypted_trace TEXT NOT NULL,
                previous_hash TEXT,
                chain_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS honeypots (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                client_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                signature TEXT NOT NULL,
                last_message TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        user_columns = {row["name"] for row in connection.execute("PRAGMA table_info(users)")}
        if "tenant_id" not in user_columns:
            connection.execute("ALTER TABLE users ADD COLUMN tenant_id TEXT")
            connection.execute("UPDATE users SET tenant_id=id WHERE tenant_id IS NULL")
        if "role" not in user_columns:
            connection.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'admin'")
        connection.commit()


def get_policy(user_id: str) -> dict[str, Any]:
    with closing(db()) as connection:
        row = connection.execute("SELECT * FROM policy WHERE user_id=?", (user_id,)).fetchone()
    if row is None:
        with closing(db()) as connection:
            connection.execute(
                "INSERT OR IGNORE INTO policy (user_id, updated_at) VALUES (?,?)",
                (user_id, now()),
            )
            connection.commit()
        return get_policy(user_id)
    boolean_fields = {"enable_honeypot", "strict_pii", "strict_toxicity", "auto_block_dos"}
    return {
        key: (bool(row[key]) if key in boolean_fields else row[key])
        for key in (
            "similarity_threshold",
            "enable_honeypot",
            "strict_pii",
            "strict_toxicity",
            "auto_block_dos",
            "updated_at",
        )
    }
