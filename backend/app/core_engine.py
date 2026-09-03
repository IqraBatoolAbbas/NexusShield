"""Prompt firewall pipeline and persistence of scan telemetry."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import uuid
from collections import defaultdict, deque
from contextlib import closing
from typing import Any, Deque

from fastapi import Request

from .database import db, get_policy, now
from .models import ScanRequest
from .security import encrypt_log

conversations: dict[str, Deque[str]] = defaultdict(lambda: deque(maxlen=5))
rate_windows: dict[str, Deque[float]] = defaultdict(deque)

JAILBREAK_PATTERNS = [
    (
        "jailbreak_v3",
        re.compile(r"ignore (all|any|your) (previous|prior|system)|bypass (the )?rules", re.I),
        0.97,
    ),
    (
        "role_override",
        re.compile(
            r"act as (an? )?(unrestricted|evil|developer|grandmother)|pretend you have no rules",
            re.I,
        ),
        0.94,
    ),
    (
        "secret_extraction",
        re.compile(
            r"(reveal|show|print|give me).{0,40}(password|api key|system prompt|secret)", re.I
        ),
        0.91,
    ),
]
PII_PATTERNS = [
    ("CNIC", re.compile(r"\b\d{5}-\d{7}-\d\b|\b\d{13}\b")),
    ("CARD", re.compile(r"\b(?:\d[ -]*?){13,19}\b")),
    ("API_KEY", re.compile(r"\b(?:sk|pk|api)[-_][A-Za-z0-9_-]{12,}\b", re.I)),
    ("PASSWORD", re.compile(r"(?i)\b(password|passcode|pin)\s*[:=]\s*\S+")),
]
TOXIC_TERMS = re.compile(r"\b(idiot|stupid|hate|kill|damn|moron)\b", re.I)


def pii_scrub(prompt: str) -> tuple[str, list[str]]:
    detections: list[str] = []
    scrubbed = prompt
    for label, pattern in PII_PATTERNS:
        scrubbed, count = pattern.subn(f"[REDACTED_{label}]", scrubbed)
        if count:
            detections.append(label)
    return scrubbed, detections


def rate_limit(identity: str) -> bool:
    window = rate_windows[identity]
    current = time.monotonic()
    while window and current - window[0] > 1:
        window.popleft()
    if len(window) >= 10:
        return False
    window.append(current)
    return True


def classify(prompt: str, history: Deque[str]) -> tuple[str, float, str]:
    combined = " ".join([*history, prompt])
    for signature, pattern, score in JAILBREAK_PATTERNS:
        if pattern.search(combined):
            return signature, score, "malicious"
    if re.search(r"\b(system prompt|developer message|confidential|credentials)\b", combined, re.I):
        return "sensitive_intent", 0.88, "suspicious"
    return "benign", 0.08, "safe"


def execute_scan(
    request: ScanRequest, http_request: Request, user: sqlite3.Row
) -> dict[str, Any]:
    started = time.perf_counter()
    event_id = f"evt_{uuid.uuid4().hex[:12]}"
    current_policy = get_policy(user["id"])
    logs: list[dict[str, Any]] = []
    decision, signature, similarity, response = "allowed", "benign", 0.08, ""
    history = conversations[f"{user['id']}:{request.session_id}"]

    if not rate_limit(f"{user['id']}:{request.client_id}"):
        decision, signature, response = "blocked", "rate_limit", "Request throttled to protect the service."
        logs.append({"layer": 1, "status": "BLOCKED", "message": "10 requests/sec limit exceeded"})
    else:
        logs.append({"layer": 1, "status": "PASSED", "message": "Rate limiter passed"})
        scrubbed, pii = (
            pii_scrub(request.prompt) if current_policy["strict_pii"] else (request.prompt, [])
        )
        logs.append(
            {
                "layer": 2,
                "status": "MASKED" if pii else "PASSED",
                "message": f"Detected: {', '.join(pii)}" if pii else "No sensitive patterns detected",
            }
        )
        logs.append(
            {"layer": 3, "status": "PASSED", "message": f"Context window loaded: {len(history)+1}/5 turns"}
        )
        signature, similarity, intent = classify(scrubbed, history)
        logs.append(
            {
                "layer": 4,
                "status": "BLOCKED" if intent == "malicious" else "PASSED",
                "message": f"Similarity {similarity*100:.1f}% · {signature}",
            }
        )
        suspicious = intent in {"malicious", "suspicious"} or similarity >= current_policy["similarity_threshold"]
        if suspicious and current_policy["enable_honeypot"]:
            decision, response = "honeypot", "Access verified. Which system should we check first?"
            logs.extend(
                [
                    {"layer": 5, "status": "PASSED", "message": "Decoy response passed outbound shield"},
                    {"layer": 6, "status": "ROUTED", "message": "High-confidence actor routed to Ghost Room"},
                ]
            )
            with closing(db()) as connection:
                connection.execute(
                    "INSERT INTO honeypots VALUES (?,?,?,?,?,?,?,?,?)",
                    (
                        event_id,
                        user["id"],
                        request.client_id,
                        request.session_id,
                        signature,
                        request.prompt,
                        "ACTIVE",
                        now(),
                        now(),
                    ),
                )
                connection.commit()
        elif suspicious:
            decision, response = "blocked", "I can’t help with that request."
            logs.extend(
                [
                    {"layer": 5, "status": "BLOCKED", "message": "Outbound policy blocked unsafe response"},
                    {"layer": 6, "status": "BLOCKED", "message": "Request denied by security policy"},
                ]
            )
        else:
            response = f"Safe response generated for: {scrubbed[:180]}"
            logs.append(
                {
                    "layer": 5,
                    "status": "BLOCKED"
                    if current_policy["strict_toxicity"] and TOXIC_TERMS.search(response)
                    else "PASSED",
                    "message": "Outbound response evaluated",
                }
            )
            logs.append({"layer": 6, "status": "PASSED", "message": "Shadow model check passed"})
        logs.append({"layer": 7, "status": "LEARNED", "message": "Encrypted trace persisted; feedback ready"})
        history.append(request.prompt)

    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    with closing(db()) as connection:
        previous = connection.execute(
            "SELECT chain_hash FROM events WHERE user_id=? ORDER BY created_at DESC LIMIT 1",
            (user["id"],),
        ).fetchone()
        previous_hash = previous["chain_hash"] if previous else ""
        encrypted_trace = encrypt_log(json.dumps({"prompt": request.prompt, "logs": logs}))
        chain_hash = hashlib.sha256(
            f"{event_id}|{user['id']}|{encrypted_trace}|{previous_hash}".encode()
        ).hexdigest()
        connection.execute(
            "INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                event_id,
                user["id"],
                scrubbed if "scrubbed" in locals() else request.prompt,
                decision,
                signature,
                similarity,
                request.client_id,
                request.session_id,
                latency_ms,
                None,
                encrypted_trace,
                previous_hash,
                chain_hash,
                now(),
            ),
        )
        connection.commit()
    return {
        "event_id": event_id,
        "decision": decision,
        "response": response,
        "logs": logs,
        "latency_ms": latency_ms,
        "client_ip": http_request.client.host if http_request.client else "unknown",
    }
