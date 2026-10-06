"""SQLite database, saved to git as a plain-text SQL dump so history diffs cleanly."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .config import ROOT

DUMP_PATH = ROOT / "data" / "residencies.sql"
DB_PATH = ROOT / "data" / "residencies.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    system_id TEXT,
    url TEXT,
    kind TEXT,
    baseline_done INTEGER DEFAULT 0,
    last_checked TEXT,
    last_ok TEXT,
    last_status TEXT,
    last_error TEXT,
    last_via TEXT,
    last_hash TEXT,
    page_signal TEXT,
    n_items INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT,
    checked_at TEXT,
    ok INTEGER,
    status TEXT,
    via TEXT,
    n_items INTEGER,
    changed INTEGER
);
CREATE TABLE IF NOT EXISTS findings (
    id TEXT PRIMARY KEY,
    source_id TEXT,
    system_id TEXT,
    kind TEXT,            -- posting | snippet
    title TEXT,
    url TEXT,
    cohort TEXT,          -- dates mentioned, e.g. "October 2027"
    relevance TEXT,       -- target | maybe | unknown | early | late
    signal TEXT,          -- open | closed | ''
    hospital_id TEXT,
    first_seen TEXT,
    last_seen TEXT,
    active INTEGER DEFAULT 1,
    missed INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    at TEXT,
    source_id TEXT,
    finding_id TEXT,
    type TEXT,            -- new_posting | new_date | now_open | upgraded | removed | page_changed | source_failing | source_recovered
    level TEXT,           -- high | medium | low
    message TEXT,
    url TEXT,
    notified INTEGER DEFAULT 0
);
"""


def open_db(dump_path: Path = DUMP_PATH, db_path: Path | None = DB_PATH) -> sqlite3.Connection:
    """Rebuilds the working database from the committed SQL dump."""
    if db_path is not None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_path.unlink(missing_ok=True)
    conn = sqlite3.connect(str(db_path) if db_path else ":memory:")
    conn.row_factory = sqlite3.Row
    if dump_path.exists():
        conn.executescript(dump_path.read_text())
    conn.executescript(SCHEMA)
    return conn


def save_db(conn: sqlite3.Connection, dump_path: Path = DUMP_PATH) -> None:
    conn.commit()
    dump_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [line for line in conn.iterdump() if not line.startswith(("BEGIN TRANSACTION", "COMMIT"))]
    dump_path.write_text("BEGIN TRANSACTION;\n" + "\n".join(lines) + "\nCOMMIT;\n")
