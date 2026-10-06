"""Writes REPORT.md (the dashboard) and the alert text used for GitHub issues."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

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


def _finding_rows(conn: sqlite3.Connection, settings: Settings, where: str) -> list[dict]:
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
        rows.append({**dict(f), "place": place, "dist": dist, "tier_rank": tier.rank if tier else 99})
    rows.sort(key=lambda r: (r["tier_rank"], r["dist"] if r["dist"] is not None else 1e9, r["first_seen"]))
    return rows


def _findings_table(rows: list[dict]) -> list[str]:
    if not rows:
        return ["_Nothing yet._", ""]
    out = ["| Miles | Hospital | Posting / text | Cohort | Signal | First seen |", "|---:|---|---|---|---|---|"]
    for r in rows:
        title = _cell(r["title"])
        link = f"[{title}]({r['url']})" if r["url"] else title
        signal = {"open": "🟢 open", "closed": "🔴 closed"}.get(r["signal"] or "", "")
        out.append(f"| {_miles(r['dist'])} | {_cell(r['place'], 70)} | {link} | {_cell(r['cohort'], 60)} | {signal} | {local(r['first_seen'], False)} |")
    return out + [""]


def build_report(conn: sqlite3.Connection, settings: Settings) -> str:
    now = utcnow()
    window = f"starting {month_label(settings.target_from)} or later"
    if settings.target_until is not None:
        window = f"starting {month_label(settings.target_from)} – {month_label(settings.target_until)}"
    last_run = conn.execute("SELECT MAX(checked_at) AS t FROM checks").fetchone()["t"]

    target = _finding_rows(conn, settings, "active = 1 AND relevance = 'target'")
    maybe = _finding_rows(conn, settings, "active = 1 AND relevance IN ('maybe', 'unknown') AND kind = 'posting'")
    early = _finding_rows(conn, settings, "active = 1 AND relevance = 'early'")

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
    out += _findings_table(target)
    out += [f"## ❓ Residency postings with an unclear start date ({len(maybe)})", "",
            "Open the link to check the cohort — these might fit.", ""]
    out += _findings_table(maybe)

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
    out += _findings_table(early)

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


def pending_alerts(conn: sqlite3.Connection, settings: Settings, mark: bool = True) -> tuple[str, str] | None:
    """Returns (issue title, issue body) for un-notified alerts, or None."""
    rows = conn.execute("SELECT * FROM events WHERE notified = 0 ORDER BY id").fetchall()
    wanted = [r for r in rows if r["level"] in settings.issue_levels]
    if mark and rows:
        conn.execute("UPDATE events SET notified = 1 WHERE notified = 0")
        conn.commit()
    if not wanted:
        return None
    wanted.sort(key=lambda r: (0 if r["level"] == "high" else 1, r["id"]))
    top = wanted[0]
    lead = "🎯 Residency cohort posted" if top["level"] == "high" else "❓ New residency posting"
    title = f"{lead}: {_cell(top['message'], 150)}"
    if len(wanted) > 1:
        title += f" (+{len(wanted) - 1} more)"
    body = ["New nurse residency activity found by the DFW Residency Watch:", ""]
    for r in wanted:
        body.append(f"- {LEVEL_ICON.get(r['level'], '')} **{r['level'].upper()}** — {r['message']}" + (f"\n  {r['url']}" if r["url"] else ""))
    repo = os.environ.get("GITHUB_REPOSITORY")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    report_link = f"[REPORT.md]({server}/{repo}/blob/HEAD/REPORT.md)" if repo else "REPORT.md"
    body += ["", f"Full list, sorted by distance: {report_link}", "",
             "_Close this issue once you've looked at it._"]
    return title, "\n".join(body)
