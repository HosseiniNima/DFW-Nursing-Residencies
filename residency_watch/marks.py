"""Your own progress on each posting: opened, applied, or not interested.

Stored in data/marks.json (separate from the database so the scheduled check and
your marks never edit the same file at the same time).
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from .config import ROOT

MARKS_PATH = ROOT / "data" / "marks.json"

STATUSES = {"opened": "👀 Opened", "applied": "✅ Applied", "skip": "🚫 Not interested"}
# When an issue has several of these labels, the first one listed wins.
LABEL_PRIORITY = ["applied", "skip", "opened"]
FINDING_MARKER_RE = re.compile(r"<!--\s*finding:\s*(\S+?)\s*-->")


def load(path: Path = MARKS_PATH) -> dict[str, dict]:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, ValueError):
        return {}


def save(marks: dict[str, dict], path: Path = MARKS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(marks, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def status_of(marks: dict[str, dict], finding_id: str) -> str | None:
    return (marks.get(finding_id) or {}).get("status")


def set_status(marks: dict[str, dict], finding_id: str, status: str | None, at: str,
               note: str | None = None, issue: int | None = None) -> bool:
    """Returns True if anything changed. status None clears the mark."""
    if status is not None and status not in STATUSES:
        raise ValueError(f"status must be one of {', '.join(STATUSES)} (or clear)")
    old = marks.get(finding_id)
    if status is None:
        if old is None:
            return False
        del marks[finding_id]
        return True
    new = dict(old or {})
    if new.get("status") != status:
        new["status"] = status
        new["at"] = at
    if note:
        new["note"] = note
    if issue:
        new["issue"] = issue
    if new == old:
        return False
    marks[finding_id] = new
    return True


def status_from_issue(labels: list[str], state: str) -> str | None:
    names = {label.strip().lower() for label in labels}
    for status in LABEL_PRIORITY:
        if status in names:
            return status
    return "opened" if state.lower() == "closed" else None


def finding_from_issue_body(body: str) -> str | None:
    m = FINDING_MARKER_RE.search(body or "")
    return m.group(1) if m else None


def short_code(finding_id: str) -> str:
    """The 6-character code shown in REPORT.md."""
    return finding_id.rsplit(":", 1)[-1][:6]


def resolve(conn: sqlite3.Connection, ref: str) -> str:
    """Finds a posting from a full id, its REPORT.md code, or an alert issue number like #12."""
    ref = ref.strip()
    if ref.startswith("#") and ref[1:].isdigit():
        row = conn.execute("SELECT id FROM findings WHERE issue_number = ?", (int(ref[1:]),)).fetchone()
        if not row:
            raise LookupError(f"no posting is linked to issue {ref}")
        return row["id"]
    if conn.execute("SELECT 1 FROM findings WHERE id = ?", (ref,)).fetchone():
        return ref
    code = ref.lower()
    if len(code) < 4:
        raise LookupError("use the 6-character code from REPORT.md")
    rows = conn.execute("SELECT id FROM findings WHERE id LIKE ?", (f"%:{code}%",)).fetchall()
    rows = [r["id"] for r in rows if short_code(r["id"]).startswith(code) or r["id"].rsplit(":", 1)[-1].startswith(code)]
    if not rows:
        raise LookupError(f"no posting has the code {ref}")
    if len(rows) > 1:
        raise LookupError(f"code {ref} matches {len(rows)} postings; use more characters")
    return rows[0]
