"""Writes REPORT.md (the dashboard) and the alert text used for GitHub issues."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from . import marks as marks_mod
from .checker import parse_iso, utcnow
from .config import Settings, month_label

CENTRAL = ZoneInfo("America/Chicago")
LEVEL_ICON = {"high": "🎯", "medium": "❓", "low": "·"}


def local(ts: str | None, with_time: bool = True) -> str:
    dt = parse_iso(ts)
    if not dt:
        return "never"
    dt = dt.astimezone(CENTRAL)
    return dt.strftime("%b %d %Y %I:%M %p").replace(" 0", " ") if with_time else dt.strftime("%b %d %Y").replace(" 0", " ")


def _cell(text: str | None, limit: int = 140) -> str:
    text = (text or "").replace("|", "/").replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _miles(m: float | None) -> str:
    return f"{m:.1f}" if m is not None else "—"


def _finding_rows(conn: sqlite3.Connection, settings: Settings, where: str, marks: dict) -> list[dict]:
    hospitals = {h.id: h for h in settings.hospitals}
    sources = {s.id: s for s in settings.sources}
    rows = []
    for f in conn.execute(f"SELECT * FROM findings WHERE {where}").fetchall():
        src = sources.get(f["source_id"])
        h = hospitals.get(f["hospital_id"])
        if h:
            place, dist, tier = h.name, h.distance_mi, h.tier
        else:
            place = f"{src.system_name if src else f['system_id']} (campus not stated)"
            dist, tier = (src.distance_mi, src.tier) if src else (None, None)
        mark = marks.get(f["id"]) or {}
        rows.append({**dict(f), "place": place, "dist": dist, "tier_rank": tier.rank if tier else 99,
                     "status": mark.get("status"), "status_at": mark.get("at"), "note": mark.get("note", "")})
    rows.sort(key=lambda r: (r["tier_rank"], r["dist"] if r["dist"] is not None else 1e9, r["first_seen"]))
    return rows


def _findings_table(rows: list[dict], show_posted: bool = False) -> list[str]:
    if not rows:
        return ["_Nothing yet._", ""]
    last = "Still posted?" if show_posted else "First seen"
    out = [f"| Miles | Hospital | Posting / text | Cohort | You | {last} | Code |", "|---:|---|---|---|---|---|---|"]
    for r in rows:
        title = _cell(r["title"])
        link = f"[{title}]({r['url']})" if r["url"] else title
        signal = {"open": "🟢 open", "closed": "🔴 closed"}.get(r["signal"] or "", "")
        cohort = " · ".join(x for x in (_cell(r["cohort"], 60), signal) if x)
        you = marks_mod.STATUSES.get(r["status"] or "", "🆕")
        if r["issue_number"]:
            you += f" (#{r['issue_number']})"
        if r["note"]:
            you += f" — {_cell(r['note'], 60)}"
        tail = ("yes" if r["active"] else f"no (last seen {local(r['last_seen'], False)})") if show_posted else local(r["first_seen"], False)
        out.append(f"| {_miles(r['dist'])} | {_cell(r['place'], 70)} | {link} | {cohort} | {you} | {tail} | `{marks_mod.short_code(r['id'])}` |")
    return out + [""]


def _split_skipped(rows: list[dict]) -> tuple[list[dict], int]:
    kept = [r for r in rows if r["status"] != "skip"]
    return kept, len(rows) - len(kept)


def _hidden_note(n: int) -> list[str]:
    return [f"_{n} more hidden because you marked them not interested._", ""] if n else []


def build_report(conn: sqlite3.Connection, settings: Settings, marks: dict | None = None) -> str:
    marks = marks_mod.load() if marks is None else marks
    now = utcnow()
    window = f"starting {month_label(settings.target_from)} or later"
    if settings.target_until is not None:
        window = f"starting {month_label(settings.target_from)} – {month_label(settings.target_until)}"
    last_run = conn.execute("SELECT MAX(checked_at) AS t FROM checks").fetchone()["t"]

    target, target_hidden = _split_skipped(_finding_rows(conn, settings, "active = 1 AND relevance = 'target'", marks))
    maybe, maybe_hidden = _split_skipped(
        _finding_rows(conn, settings, "active = 1 AND relevance IN ('maybe', 'unknown') AND kind = 'posting'", marks))
    early, early_hidden = _split_skipped(_finding_rows(conn, settings, "active = 1 AND relevance = 'early'", marks))
    tracked = [r for r in _finding_rows(conn, settings, "1", marks) if r["status"] in ("applied", "opened")]
    tracked.sort(key=lambda r: (0 if r["status"] == "applied" else 1, r["dist"] if r["dist"] is not None else 1e9))

    out = [
        "# DFW Nurse Residency Watch",
        "",
        f"Looking for residency cohorts **{window}**. "
        f"Home location: **{settings.home_label}**. "
        f"Last check: **{local(last_run)}** (Central). Updated automatically — see [README](README.md).",
        "",
    ]
    if settings.home is None:
        out += ["> ⚠️ Home location isn't set, so hospitals aren't ranked by distance and everything is checked once a day. "
                "Set `HOME_ZIP` (see README).", ""]

    out += [f"## 🎯 Cohorts you can apply for ({len(target)})", "",
            "Postings or announcements that mention a start date in your window, closest first.", ""]
    out += _findings_table(target) + _hidden_note(target_hidden)
    out += [f"## ❓ Residency postings with an unclear start date ({len(maybe)})", "",
            "Open the link to check the cohort — these might fit.", ""]
    out += _findings_table(maybe) + _hidden_note(maybe_hidden)
    applied = sum(1 for r in tracked if r["status"] == "applied")
    out += [f"## 📝 Your applications ({applied} applied, {len(tracked) - applied} opened)", "",
            "Postings you've marked. To mark one, add the label `applied`, `opened` or `skip` to its alert issue, "
            "or use the **Code** column with *Actions → Track applications → Run workflow* (see README).", ""]
    out += _findings_table(tracked, show_posted=True) if tracked else ["_Nothing marked yet._", ""]

    recent = conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT 40").fetchall()
    out += ["## 🔔 Recent activity", ""]
    if recent:
        for e in recent:
            msg = _cell(e["message"], 220)
            link = f" ([link]({e['url']}))" if e["url"] else ""
            out.append(f"- {LEVEL_ICON.get(e['level'], '·')} {local(e['at'])} — {msg}{link}")
    else:
        out.append("_No activity yet._")
    out.append("")

    out += [f"## 📅 Earlier cohorts currently posted ({len(early)})", "",
            "Too early for you, but they show when each hospital opens applications — expect your cohort to post about a year later.", ""]
    out += _findings_table(early) + _hidden_note(early_hidden)

    out += ["## 🏥 Hospitals by priority", "",
            "| # | Miles | Hospital | City | System | Checked |", "|---:|---:|---|---|---|---|"]
    hospitals = sorted(settings.hospitals, key=lambda h: (h.tier.rank, h.distance_mi if h.distance_mi is not None else 1e9, h.name))
    for i, h in enumerate(hospitals, 1):
        every = h.tier.check_every_hours
        freq = "daily" if every >= 24 else f"every {every:g}h"
        star = " ⭐" if h.id in settings.favorites else ""
        out.append(f"| {i} | {_miles(h.distance_mi)} | {h.name}{star} | {h.city} | {h.system_name} | {h.tier.name}, {freq} |")
    out.append("")

    out += ["## 🩺 Source health", "",
            "Every page that gets checked. ❌ rows usually mean the website moved the page — update the URL in `hospitals.yaml`.", "",
            "| Status | Source | Last checked | Found | Note |", "|---|---|---|---:|---|"]
    rows = {r["id"]: r for r in conn.execute("SELECT * FROM sources").fetchall()}
    for src in sorted(settings.sources, key=lambda s: (s.tier.rank, s.system_name)):
        r = rows.get(src.id)
        if r is None or not r["last_checked"]:
            status, note, checked, found = "⏳", "not checked yet", "never", ""
        elif r["last_status"] == "ok":
            status = "✅"
            note = f"via {r['last_via']}" + (" · says open" if r["page_signal"] == "open" else "")
            checked, found = local(r["last_checked"]), str(r["n_items"] or 0)
        else:
            status = "❌"
            note = _cell(r["last_error"], 80) + (f" · failing {r['consecutive_failures']}× in a row" if r["consecutive_failures"] else "")
            checked, found = local(r["last_checked"]), ""
        if not src.verified:
            note += " · unverified URL"
        out.append(f"| {status} | [{src.system_name} — {src.id}]({src.url}) | {checked} | {found} | {_cell(note, 120)} |")
    out += ["", f"_Generated {local(now.isoformat())} Central._", ""]
    return "\n".join(out)


def _report_link() -> str:
    repo = os.environ.get("GITHUB_REPOSITORY")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    return f"[REPORT.md]({server}/{repo}/blob/HEAD/REPORT.md)" if repo else "REPORT.md"


HOW_TO_MARK = (
    "**Track it with a label:** `applied` once you've applied · `opened` once you've looked · "
    "`skip` if you're not interested (no more alerts about it). Closing the issue also counts as opened."
)


def pending_alerts(conn: sqlite3.Connection, settings: Settings, marks: dict | None = None,
                   mark_sent: bool = True) -> list[dict]:
    """One entry per posting with un-notified alerts.

    Each entry: {"finding_id", "issue" (existing issue number to comment on, or None), "title", "body"}.
    """
    marks = marks_mod.load() if marks is None else marks
    rows = conn.execute("SELECT * FROM events WHERE notified = 0 ORDER BY id").fetchall()
    if mark_sent and rows:
        conn.execute("UPDATE events SET notified = 1 WHERE notified = 0")
        conn.commit()
    wanted = [r for r in rows if r["level"] in settings.issue_levels
              and marks_mod.status_of(marks, r["finding_id"] or "") != "skip"]

    grouped: dict[str | None, list] = {}
    for r in wanted:
        grouped.setdefault(r["finding_id"], []).append(r)

    rows_by_id = {r["id"]: r for r in _finding_rows(conn, settings, "1", marks)}
    alerts = []
    for fid, events in grouped.items():
        events.sort(key=lambda e: (0 if e["level"] == "high" else 1, e["id"]))
        lines = [f"- {LEVEL_ICON.get(e['level'], '')} {e['message']}" + (f"\n  {e['url']}" if e["url"] else "")
                 for e in events]
        f = rows_by_id.get(fid) if fid else None
        if f and f["issue_number"]:
            alerts.append({"finding_id": fid, "issue": f["issue_number"], "title": "",
                           "body": "Update from the DFW Residency Watch:\n\n" + "\n".join(lines)})
            continue
        icon = LEVEL_ICON.get(events[0]["level"], "")
        if f:
            dist = f" ({f['dist']:.1f} mi)" if f["dist"] is not None else ""
            title = f"{icon} {f['place']}{dist}: {_cell(f['title'], 150)}"
            link = f"[{_cell(f['title'], 200)}]({f['url']})" if f["url"] else _cell(f["title"], 200)
            body = [f"**{f['place']}**{dist}", "",
                    f"**Posting:** {link}",
                    f"**Cohort:** {f['cohort'] or 'not stated — open the posting to check'}",
                    f"**Code:** `{marks_mod.short_code(fid)}`", "",
                    *lines, "", "---", HOW_TO_MARK, "",
                    f"Everything found so far, closest first: {_report_link()}",
                    f"<!-- finding:{fid} -->"]
        else:
            title = f"{icon} Residency watch: {_cell(events[0]['message'], 150)}"
            body = [*lines, "", f"Everything found so far, closest first: {_report_link()}"]
        alerts.append({"finding_id": fid, "issue": None, "title": title[:250], "body": "\n".join(body)})
    return alerts
