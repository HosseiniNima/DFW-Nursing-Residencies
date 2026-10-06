"""Checks the sources that are due and records what changed."""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timedelta, timezone

from . import extract, workday
from .config import Hospital, Settings, Source
from .fetch import Fetcher

# A tier's interval is shortened by this much so cron jitter doesn't skip a run.
SCHEDULE_SLACK = timedelta(minutes=45)
# A posting has to be missing this many successful checks in a row before it counts as removed.
MISSES_BEFORE_REMOVED = 2


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def parse_iso(s: str | None) -> datetime | None:
    return datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def is_due(src: Source, last_checked: str | None, now: datetime) -> bool:
    last = parse_iso(last_checked)
    return last is None or now - last >= timedelta(hours=src.tier.check_every_hours) - SCHEDULE_SLACK


def match_hospital(text: str, src: Source, settings: Settings, strict: bool = False) -> Hospital | None:
    """Ties a posting to a campus by name/city words, preferring the closest match.

    strict: only accept an explicit name/city match (used to drop postings outside DFW).
    """
    if src.hospitals:
        candidates = src.hospitals
    else:  # aggregator: only systems whose name appears in the text
        systems = [s for s in settings.systems if s.hospitals and any(a.lower() in text.lower() for a in s.aliases)]
        candidates = [h for s in systems for h in s.hospitals]
    hits = []
    for h in candidates:
        words = [h.name, *h.match]
        if any(re.search(r"\b" + re.escape(w) + r"\b", text, re.I) for w in words):
            # A full hospital name beats a bare city match.
            hits.append((0 if re.search(re.escape(h.name), text, re.I) else 1, h.distance_mi or 0, h))
    if hits:
        return min(hits, key=lambda t: (t[0], t[1]))[2]
    if not strict and not src.hospitals and len({h.system_id for h in candidates}) == 1 and candidates:
        return min(candidates, key=lambda h: h.distance_mi or 0)
    return None


def _url_words(url: str) -> str:
    """Job URLs often carry the campus city ("...-mother-baby-rockwall-tx/")."""
    path = url.split("?", 1)[0].split("://", 1)[-1].split("/", 1)[-1] if url else ""
    return re.sub(r"[-_/+%]+", " ", path)


def _level_for_new(relevance: str, kind: str, baseline: bool) -> str | None:
    if relevance == "target":
        return "high"
    if relevance == "maybe":
        return "medium"
    if relevance == "unknown" and kind == "posting" and not baseline:
        return "medium"
    return None


def _describe(src: Source, item_title: str, cohort: str, hospital: Hospital | None) -> str:
    where = src.system_name
    if hospital:
        where = hospital.name
        if hospital.distance_mi is not None:
            where += f" ({hospital.distance_mi:.1f} mi)"
    cohort_part = f" — cohort: {cohort}" if cohort else ""
    return f"{where}: {item_title}{cohort_part}"


def check_source(conn: sqlite3.Connection, settings: Settings, src: Source, fetcher: Fetcher, now: datetime) -> dict:
    now_s = iso(now)
    now_idx = now.year * 12 + now.month - 1
    row = conn.execute("SELECT * FROM sources WHERE id = ?", (src.id,)).fetchone()
    if row is None:
        conn.execute("INSERT INTO sources (id, system_id, url, kind) VALUES (?, ?, ?, ?)", (src.id, src.system_id, src.url, src.kind))
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (src.id,)).fetchone()
    elif row["url"] != src.url:  # URL edited in hospitals.yaml: start a fresh baseline
        conn.execute("UPDATE sources SET url = ?, kind = ?, baseline_done = 0, last_hash = NULL WHERE id = ?", (src.url, src.kind, src.id))
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (src.id,)).fetchone()

    if src.kind == "workday":
        res, wd_items = workday.search(fetcher, src.url, src.search, now_idx)
    else:
        res = fetcher.get(src.url, src.render, visible_text_len=lambda html: len(extract.visible_text(html)))
    events: list[tuple] = []

    def event(type_, level, message, finding_id=None, url=None):
        events.append((now_s, src.id, finding_id, type_, level, message, url or src.url))

    if not res.ok:
        fails = (row["consecutive_failures"] or 0) + 1
        conn.execute(
            "UPDATE sources SET last_checked=?, last_status='error', last_error=?, last_via=?, consecutive_failures=? WHERE id=?",
            (now_s, res.error, res.via, fails, src.id),
        )
        conn.execute(
            "INSERT INTO checks (source_id, checked_at, ok, status, via, n_items, changed) VALUES (?,?,?,?,?,?,?)",
            (src.id, now_s, 0, res.error, res.via, 0, 0),
        )
        if fails == 3:
            event("source_failing", "low", f"{src.system_name}: {src.url} has failed 3 checks in a row ({res.error})")
        conn.executemany("INSERT INTO events (at, source_id, finding_id, type, level, message, url) VALUES (?,?,?,?,?,?,?)", events)
        return {"source": src.id, "ok": False, "error": res.error, "events": len(events)}

    if src.kind == "workday":
        page = extract.PageResult("", extract.items_hash(wd_items), wd_items, "")
    else:
        page = extract.analyze(res.html, res.final_url or src.url, src.kind, now_idx)
    if src.dfw_only or not src.hospitals:
        page.items = [i for i in page.items
                      if match_hospital(f"{i.title} {i.context} {_url_words(i.url)}", src, settings, strict=True)]
    baseline = not row["baseline_done"]
    if (row["consecutive_failures"] or 0) >= 3:
        event("source_recovered", "low", f"{src.system_name}: {src.url} is working again")

    seen_ids = set()
    for item in page.items:
        relevance = extract.classify(item.cohorts, settings.target_from, settings.target_until)
        cohort = ", ".join(c.label for c in item.cohorts)
        hospital = match_hospital(f"{item.title} {item.context} {_url_words(item.url)}", src, settings)
        fid = f"{src.id}:{item.key}"
        seen_ids.add(fid)
        old = conn.execute("SELECT * FROM findings WHERE id = ?", (fid,)).fetchone()
        if old is None:
            conn.execute(
                "INSERT INTO findings (id, source_id, system_id, kind, title, url, cohort, relevance, signal, hospital_id, first_seen, last_seen, active, missed)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1,0)",
                (fid, src.id, src.system_id, item.kind, item.title, item.url, cohort, relevance, item.signal,
                 hospital.id if hospital else None, now_s, now_s),
            )
            level = _level_for_new(relevance, item.kind, baseline)
            if level:
                kind = "new_posting" if item.kind == "posting" else "new_date"
                event(kind, level, _describe(src, item.title, cohort, hospital), fid, item.url)
            continue

        conn.execute(
            "UPDATE findings SET last_seen=?, active=1, missed=0, cohort=?, relevance=?, signal=?, hospital_id=COALESCE(?, hospital_id), url=? WHERE id=?",
            (now_s, cohort, relevance, item.signal, hospital.id if hospital else None, item.url, fid),
        )
        if not old["active"] and relevance in ("target", "maybe"):
            event("reposted", "high" if relevance == "target" else "medium", "Back up: " + _describe(src, item.title, cohort, hospital), fid, item.url)
        elif old["relevance"] != "target" and relevance == "target":
            event("upgraded", "high", "Now lists a target cohort: " + _describe(src, item.title, cohort, hospital), fid, item.url)
        elif relevance in ("target", "maybe") and item.signal == "open" and old["signal"] != "open":
            event("now_open", "high" if relevance == "target" else "medium", "Applications look open: " + _describe(src, item.title, cohort, hospital), fid, item.url)

    for old in conn.execute("SELECT * FROM findings WHERE source_id = ? AND active = 1", (src.id,)).fetchall():
        if old["id"] in seen_ids:
            continue
        missed = old["missed"] + 1
        active = 0 if missed >= MISSES_BEFORE_REMOVED else 1
        conn.execute("UPDATE findings SET missed=?, active=? WHERE id=?", (missed, active, old["id"]))
        if not active and old["relevance"] in ("target", "maybe"):
            level = "medium" if old["relevance"] == "target" else "low"
            event("removed", level, f"No longer listed (applications may have closed): {src.system_name}: {old['title']}", old["id"], old["url"])

    changed = bool(row["last_hash"]) and row["last_hash"] != page.text_hash
    if changed and src.kind == "page" and not any(e[4] in ("high", "medium") for e in events):
        event("page_changed", "low", f"{src.system_name}: residency page content changed — worth a look")

    conn.execute(
        "UPDATE sources SET last_checked=?, last_ok=?, last_status='ok', last_error=NULL, last_via=?, last_hash=?, page_signal=?,"
        " n_items=?, consecutive_failures=0, baseline_done=1 WHERE id=?",
        (now_s, now_s, res.via, page.text_hash, page.page_signal, len(page.items), src.id),
    )
    conn.execute(
        "INSERT INTO checks (source_id, checked_at, ok, status, via, n_items, changed) VALUES (?,?,?,?,?,?,?)",
        (src.id, now_s, 1, f"HTTP {res.status}", res.via, len(page.items), int(changed)),
    )
    conn.executemany("INSERT INTO events (at, source_id, finding_id, type, level, message, url) VALUES (?,?,?,?,?,?,?)", events)
    return {"source": src.id, "ok": True, "items": len(page.items), "events": len(events), "via": res.via}


def run(conn: sqlite3.Connection, settings: Settings, force: bool = False, only: set[str] | None = None,
        fetcher: Fetcher | None = None, now: datetime | None = None) -> list[dict]:
    now = now or utcnow()
    own_fetcher = fetcher is None
    fetcher = fetcher or Fetcher(settings.timeout, settings.per_host_delay, settings.browser_fallback)
    results = []
    # Closest sources first, so the important ones finish even if a run gets cut short.
    ordered = sorted(settings.sources, key=lambda s: (s.tier.rank, s.distance_mi if s.distance_mi is not None else 1e9))
    try:
        for src in ordered:
            if only and src.id not in only and src.system_id not in only:
                continue
            row = conn.execute("SELECT last_checked FROM sources WHERE id = ?", (src.id,)).fetchone()
            if not force and not only and not is_due(src, row["last_checked"] if row else None, now):
                continue
            try:
                result = check_source(conn, settings, src, fetcher, now)
            except Exception as exc:  # one broken page must not stop the rest
                result = {"source": src.id, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
            conn.commit()
            results.append(result)
            print(f"[{src.tier.name}] {src.id}: {result}")
    finally:
        if own_fetcher:
            fetcher.close()
    # Sources removed from hospitals.yaml: forget them and what they found.
    configured = [s.id for s in settings.sources]
    marks = ",".join("?" * len(configured))
    conn.execute(f"DELETE FROM findings WHERE source_id NOT IN ({marks})", configured)
    conn.execute(f"DELETE FROM sources WHERE id NOT IN ({marks})", configured)
    cutoff = iso(now - timedelta(days=settings.keep_check_history_days))
    conn.execute("DELETE FROM checks WHERE checked_at < ?", (cutoff,))
    conn.commit()
    return results
