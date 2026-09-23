"""SQLite persistence for dog state. Independent of Gemini and the warehouse."""

from __future__ import annotations

import os
import sqlite3
import threading
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_PATH = _ROOT / "var" / "waggy_state.sqlite"
_LOCK = threading.RLock()
_CONN: sqlite3.Connection | None = None
_CONN_PATH: str | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS dogs (
    dog_id TEXT PRIMARY KEY,
    owner_id TEXT,
    name TEXT NOT NULL,
    primary_breed TEXT,
    secondary_breed TEXT,
    breed_split_pct REAL,
    birthday TEXT,
    age_years REAL,
    weight_kg REAL,
    sex TEXT,
    activity_level TEXT,
    current_environment TEXT,
    height_cm REAL,
    bcs REAL,
    observed_conditions TEXT NOT NULL DEFAULT '[]',
    monthly_budget REAL,
    breed_input_state TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    dog_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL,
    kind TEXT,
    value TEXT,
    payload TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    created_at TEXT NOT NULL,
    session_id TEXT,
    correlation_id TEXT,
    confirmed INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    observed_at TEXT,
    recorded_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_dog_ts ON events (dog_id, timestamp, event_id);

CREATE TABLE IF NOT EXISTS preferences (
    preference_id TEXT PRIMARY KEY,
    dog_id TEXT NOT NULL,
    category TEXT NOT NULL,
    value TEXT NOT NULL,
    source TEXT NOT NULL,
    status TEXT NOT NULL,
    event_id TEXT,
    created_at TEXT NOT NULL,
    superseded INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_prefs_dog ON preferences (dog_id, superseded, created_at);

CREATE TABLE IF NOT EXISTS analyses (
    analysis_id TEXT PRIMARY KEY,
    dog_id TEXT NOT NULL,
    analysis_signature TEXT NOT NULL,
    engine_version TEXT,
    warehouse_version TEXT,
    input_snapshot TEXT NOT NULL DEFAULT '{}',
    result_digest TEXT NOT NULL DEFAULT '{}',
    result_status TEXT NOT NULL DEFAULT 'ok',
    created_at TEXT NOT NULL,
    correlation_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_analyses_dog_ts ON analyses (dog_id, created_at, analysis_id);

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    dog_id TEXT,
    analysis_signature TEXT NOT NULL,
    selected_bundle_id TEXT,
    messages TEXT NOT NULL DEFAULT '[]',
    policy_version TEXT,
    provider TEXT,
    model TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def state_path() -> Path:
    raw = os.environ.get("WAGGY_STATE_PATH")
    if raw:
        return Path(raw)
    return _DEFAULT_PATH


def close_connection() -> None:
    global _CONN, _CONN_PATH
    with _LOCK:
        if _CONN is not None:
            _CONN.close()
        _CONN = None
        _CONN_PATH = None


def connect() -> sqlite3.Connection:
    global _CONN, _CONN_PATH
    path = str(state_path())
    with _LOCK:
        if _CONN is not None and _CONN_PATH == path:
            return _CONN
        if _CONN is not None:
            _CONN.close()
            _CONN = None
        dest = Path(path)
        if dest.parent and str(dest.parent) not in {"", "."}:
            dest.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(SCHEMA)
        _ensure_additive_columns(conn)
        _CONN = conn
        _CONN_PATH = path
        return conn


def _ensure_additive_columns(conn: sqlite3.Connection) -> None:
    """Add nullable columns to existing SQLite files. Does not backfill times."""
    _add_column_if_missing(conn, "dogs", "breed_input_state", "TEXT")
    _add_column_if_missing(conn, "events", "observed_at", "TEXT")
    _add_column_if_missing(conn, "events", "recorded_at", "TEXT")


def _add_column_if_missing(conn: sqlite3.Connection, table: str, column: str, decl: str) -> None:
    existing = {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")


def locked() -> threading.RLock:
    return _LOCK
