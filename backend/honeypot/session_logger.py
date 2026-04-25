"""SQLite session logging for the MIRAGE SSH honeypot."""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "mirage.db"
_DB_LOCK = threading.Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            ip_address TEXT NOT NULL,
            username_tried TEXT,
            password_tried TEXT,
            commands_run TEXT NOT NULL DEFAULT '[]',
            start_time TEXT NOT NULL,
            end_time TEXT,
            is_active INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    conn.commit()


def create_session(ip_address: str, username_tried: str, password_tried: str) -> str:
    """Create and persist a new active session."""
    session_id = str(uuid.uuid4())
    with _DB_LOCK:
        with _get_connection() as conn:
            _ensure_schema(conn)
            conn.execute(
                """
                INSERT INTO sessions (
                    session_id,
                    ip_address,
                    username_tried,
                    password_tried,
                    commands_run,
                    start_time,
                    is_active
                ) VALUES (?, ?, ?, ?, '[]', ?, 1)
                """,
                (session_id, ip_address, username_tried, password_tried, _utc_now()),
            )
            conn.commit()
    return session_id


def log_command(
    session_id: str,
    command: str,
    response: str,
    prediction_data: dict | None = None,
) -> None:
    """Append command/response interaction to commands_run JSON array."""
    entry = {"timestamp": _utc_now(), "command": command, "response": response}
    if prediction_data is not None:
        entry["prediction_data"] = prediction_data
    with _DB_LOCK:
        with _get_connection() as conn:
            _ensure_schema(conn)
            row = conn.execute(
                "SELECT commands_run FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if row is None:
                return
            existing = json.loads(row["commands_run"] or "[]")
            existing.append(entry)
            conn.execute(
                "UPDATE sessions SET commands_run = ? WHERE session_id = ?",
                (json.dumps(existing), session_id),
            )
            conn.commit()


def end_session(session_id: str) -> None:
    """Mark session as inactive and store end timestamp."""
    with _DB_LOCK:
        with _get_connection() as conn:
            _ensure_schema(conn)
            conn.execute(
                """
                UPDATE sessions
                SET end_time = ?, is_active = 0
                WHERE session_id = ?
                """,
                (_utc_now(), session_id),
            )
            conn.commit()


def get_sessions(limit: int = 100, offset: int = 0, active_only: bool | None = None) -> list[dict]:
    """Return recent sessions (most recent first)."""
    where = ""
    params: list[object] = []
    if active_only is True:
        where = "WHERE is_active = 1"
    elif active_only is False:
        where = "WHERE is_active = 0"
    params.extend([int(limit), int(offset)])

    with _DB_LOCK:
        with _get_connection() as conn:
            _ensure_schema(conn)
            rows = conn.execute(
                f"""
                SELECT session_id, ip_address, username_tried, password_tried,
                       start_time, end_time, is_active
                FROM sessions
                {where}
                ORDER BY start_time DESC
                LIMIT ? OFFSET ?
                """,
                params,
            ).fetchall()

    return [dict(row) for row in rows]


def get_session(session_id: str) -> dict | None:
    """Return a single session row including parsed commands_run."""
    with _DB_LOCK:
        with _get_connection() as conn:
            _ensure_schema(conn)
            row = conn.execute(
                """
                SELECT session_id, ip_address, username_tried, password_tried,
                       commands_run, start_time, end_time, is_active
                FROM sessions
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
            if row is None:
                return None
            data = dict(row)
            data["commands_run"] = json.loads(data.get("commands_run") or "[]")
            return data
