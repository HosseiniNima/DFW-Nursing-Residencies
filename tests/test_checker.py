from datetime import datetime, timezone
from pathlib import Path

from residency_watch import checker, config, db, report
from residency_watch.fetch import FetchResult

FIX = Path(__file__).parent / "fixtures"

CONFIG = """
home: {lat: 33.0198, lon: -96.6989}   # Plano
target_from: "2027-08"
priority_tiers:
  - {name: Near, max_miles: 15, check_every_hours: 3}
  - {name: Far, max_miles: 9999, check_every_hours: 24}
alerts: {issue_levels: [high, medium]}
fetch: {per_host_delay_seconds: 0, browser_fallback: false}
"""
HOSPITALS = """
systems:
  - id: thr
    name: Texas Health Resources
    aliases: [Texas Health]
    sources:
      - {id: thr-jobs, kind: jobs, url: https://jobs.example.org/search}
    hospitals:
      - {id: thr-plano, name: Texas Health Plano, city: Plano, lat: 33.0440, lon: -96.8370}
      - {id: thr-dallas, name: Texas Health Dallas, city: Dallas, lat: 32.8810, lon: -96.7630}
      - {id: thr-arlington, name: Texas Health Arlington, city: Arlington, lat: 32.7470, lon: -97.1170}
  - id: far
    name: Far Hospital
    sources:
      - {id: far-page, kind: page, url: https://far.example.org/residency}
    hospitals:
      - {id: far-1, name: Far Hospital, city: Weatherford, lat: 32.76, lon: -97.79}
"""


class FakeFetcher:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def get(self, url, render="auto", visible_text_len=None):
        self.calls.append(url)
        html = self.pages.get(url)
        if html is None:
            return FetchResult(url, url, 404, "", "http", "HTTP 404")
        return FetchResult(url, url, 200, html, "http")

    def close(self):
        pass


def setup(tmp_path, monkeypatch):
    for var in ("HOME_ZIP", "HOME_LAT", "HOME_LON"):
        monkeypatch.delenv(var, raising=False)
    (tmp_path / "config.yaml").write_text(CONFIG)
    (tmp_path / "hospitals.yaml").write_text(HOSPITALS)
    settings = config.load(tmp_path / "config.yaml", tmp_path / "hospitals.yaml")
    conn = db.open_db(tmp_path / "dump.sql", None)
    return settings, conn


def test_tiers_and_schedule(tmp_path, monkeypatch):
    settings, conn = setup(tmp_path, monkeypatch)
    tiers = {h.id: h.tier.name for h in settings.hospitals}
    assert tiers["thr-plano"] == "Near" and tiers["far-1"] == "Far"
    fetcher = FakeFetcher({"https://jobs.example.org/search": (FIX / "jobs_board.html").read_text(),
                           "https://far.example.org/residency": (FIX / "program_page.html").read_text()})
    t0 = datetime(2026, 10, 6, 12, tzinfo=timezone.utc)
    checker.run(conn, settings, marks={}, save_marks=False, fetcher=fetcher, now=t0)
    assert len(fetcher.calls) == 2
    # 3 hours later only the near source is due
    checker.run(conn, settings, marks={}, save_marks=False, fetcher=fetcher, now=t0.replace(hour=15))
    assert fetcher.calls[2:] == ["https://jobs.example.org/search"]


def test_findings_alerts_and_persistence(tmp_path, monkeypatch):
    settings, conn = setup(tmp_path, monkeypatch)
    pages = {"https://jobs.example.org/search": (FIX / "jobs_board.html").read_text(),
             "https://far.example.org/residency": (FIX / "program_page.html").read_text()}
    fetcher = FakeFetcher(pages)
    t0 = datetime(2026, 10, 6, 12, tzinfo=timezone.utc)
    checker.run(conn, settings, marks={}, save_marks=False, fetcher=fetcher, now=t0)

    f = conn.execute("SELECT * FROM findings WHERE title LIKE '%October 2027%' AND kind='posting'").fetchone()
    assert f["relevance"] == "target" and f["hospital_id"] == "thr-dallas"

    events = conn.execute("SELECT level, type, message FROM events").fetchall()
    highs = [e for e in events if e["level"] == "high"]
    # October 2027 posting + October 2027 page snippet
    assert len(highs) == 2
    # first check is a baseline: unclear-date postings don't alert yet
    assert not any("Fall Cohort" in e["message"] for e in events)

    alerts = report.pending_alerts(conn, settings, marks={})
    # Oct 2027 posting, Oct 2027 page date, Summer 2027 (maybe) posting
    assert len(alerts) == 3 and all(a["issue"] is None for a in alerts)  # one issue per posting
    posting = next(a for a in alerts if "MICU" in a["title"])
    assert posting["title"].startswith("🎯") and "October 2027" in posting["body"]
    assert f"<!-- finding:{f['id']} -->" in posting["body"]
    assert report.pending_alerts(conn, settings, marks={}) == []  # already notified

    # A new unclear-date posting after the baseline → medium alert; the Oct 2027 one disappears twice → removed
    pages["https://jobs.example.org/search"] = pages["https://jobs.example.org/search"].replace(
        '<li><a href="/job/222/gn-residency-icu-oct-2027">Graduate Nurse (GN) Residency - MICU - October 2027</a><span>Dallas, TX</span></li>',
        '<li><a href="/job/666/new-grad">New Grad RN Residency - Cardiac</a><span>Plano, TX</span></li>')
    checker.run(conn, settings, marks={}, save_marks=False, fetcher=fetcher, now=t0.replace(hour=15), force=True)
    checker.run(conn, settings, marks={}, save_marks=False, fetcher=fetcher, now=t0.replace(hour=18), force=True)
    types = [(e["type"], e["level"]) for e in conn.execute("SELECT * FROM events WHERE notified = 0")]
    assert ("new_posting", "medium") in types
    assert ("removed", "medium") in types

    md = report.build_report(conn, settings, marks={})
    assert "Cohorts you can apply for" in md and "Texas Health Plano" in md

    # Save and reload from the SQL dump
    db.save_db(conn, tmp_path / "dump.sql")
    conn2 = db.open_db(tmp_path / "dump.sql", None)
    assert conn2.execute("SELECT COUNT(*) FROM findings").fetchone()[0] == conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0]


def test_failing_source(tmp_path, monkeypatch):
    settings, conn = setup(tmp_path, monkeypatch)
    fetcher = FakeFetcher({})
    t0 = datetime(2026, 10, 6, 12, tzinfo=timezone.utc)
    for hour in (12, 15, 18):
        checker.run(conn, settings, marks={}, save_marks=False, fetcher=fetcher, now=t0.replace(hour=hour), force=True)
    row = conn.execute("SELECT * FROM sources WHERE id='thr-jobs'").fetchone()
    assert row["consecutive_failures"] == 3 and row["last_error"] == "HTTP 404"
    assert conn.execute("SELECT COUNT(*) FROM events WHERE type='source_failing'").fetchone()[0] == 2
    assert "❌" in report.build_report(conn, settings, marks={})


def test_dfw_only_drops_other_cities(tmp_path, monkeypatch):
    settings, conn = setup(tmp_path, monkeypatch)
    src = settings.sources[0]
    src.dfw_only = True
    html = """<ul>
      <li><a href="/a/job/1">New Grad Nurse Residency</a> Fort Worth, TX</li>
      <li><a href="/b/job/2">New Grad RN Resident PCU</a> El Paso, TX</li>
      <li><a href="/c/job/3">Nurse Residency - Med Surg</a> Plano, TX</li></ul>"""
    fetcher = FakeFetcher({src.url: html, "https://far.example.org/residency": "<p>x</p>"})
    checker.run(conn, settings, marks={}, save_marks=False, fetcher=fetcher, now=datetime(2026, 10, 6, 12, tzinfo=timezone.utc))
    titles = {r["title"] for r in conn.execute("SELECT title FROM findings WHERE source_id = ?", (src.id,))}
    assert titles == {"Nurse Residency - Med Surg"}  # Fort Worth isn't a THR campus in this test config


def test_marks_issues_and_skip(tmp_path, monkeypatch):
    from residency_watch import marks as marks_mod

    settings, conn = setup(tmp_path, monkeypatch)
    pages = {"https://jobs.example.org/search": (FIX / "jobs_board.html").read_text(),
             "https://far.example.org/residency": "<p>nothing</p>"}
    fetcher = FakeFetcher(pages)
    marks = {}
    t0 = datetime(2026, 10, 6, 12, tzinfo=timezone.utc)
    checker.run(conn, settings, marks=marks, save_marks=False, fetcher=fetcher, now=t0)
    fid = conn.execute("SELECT id FROM findings WHERE title LIKE '%October 2027%'").fetchone()["id"]
    report.pending_alerts(conn, settings, marks=marks)
    conn.execute("UPDATE findings SET issue_number = 7 WHERE id = ?", (fid,))

    # Mark it applied: shows under "Your applications", findable by code and by issue number
    assert marks_mod.resolve(conn, marks_mod.short_code(fid)) == fid
    assert marks_mod.resolve(conn, "#7") == fid
    marks_mod.set_status(marks, fid, "applied", "2026-10-07T00:00:00Z", note="sent resume")
    md = report.build_report(conn, settings, marks=marks)
    assert "1 applied" in md and "✅ Applied (#7) — sent resume" in md

    # Later news about a posting that already has an issue becomes a comment on that issue
    pages["https://jobs.example.org/search"] = pages["https://jobs.example.org/search"].replace("October 2027", "October 2027 (apply now)")
    conn.execute("INSERT INTO events (at, source_id, finding_id, type, level, message, url) VALUES ('2026-10-07T00:00:00Z','thr-jobs',?,'now_open','high','open!','u')", (fid,))
    alerts = report.pending_alerts(conn, settings, marks=marks)
    assert alerts == [{"finding_id": fid, "issue": 7, "title": "", "body": alerts[0]["body"]}]

    # Not interested: no more alerts, hidden from the main list
    marks_mod.set_status(marks, fid, "skip", "2026-10-08T00:00:00Z")
    conn.execute("INSERT INTO events (at, source_id, finding_id, type, level, message, url) VALUES ('2026-10-07T00:00:00Z','thr-jobs',?,'now_open','high','open!','u')", (fid,))
    assert report.pending_alerts(conn, settings, marks=marks) == []
    md = report.build_report(conn, settings, marks=marks)
    assert "hidden because you marked them not interested" in md


def test_status_from_issue():
    from residency_watch import marks as marks_mod

    assert marks_mod.status_from_issue(["residency-alert", "applied", "opened"], "open") == "applied"
    assert marks_mod.status_from_issue(["residency-alert"], "closed") == "opened"
    assert marks_mod.status_from_issue(["residency-alert", "Skip"], "closed") == "skip"
    assert marks_mod.status_from_issue(["residency-alert"], "open") is None
    assert marks_mod.finding_from_issue_body("text\n<!-- finding:thr-jobs:abc123 -->") == "thr-jobs:abc123"


def test_reworded_title_keeps_identity(tmp_path, monkeypatch):
    settings, conn = setup(tmp_path, monkeypatch)
    page = '<li><a href="/x/new-grad/ABC/job/">New Grad Nurse Residency Plano, TX Posted 21 days ago</a></li>'
    pages = {"https://jobs.example.org/search": page, "https://far.example.org/residency": "<p>x</p>"}
    fetcher = FakeFetcher(pages)
    marks = {}
    t0 = datetime(2026, 10, 6, 12, tzinfo=timezone.utc)
    checker.run(conn, settings, marks=marks, save_marks=False, fetcher=fetcher, now=t0)
    (fid,) = [r["id"] for r in conn.execute("SELECT id FROM findings")]
    assert conn.execute("SELECT title FROM findings").fetchone()["title"] == "New Grad Nurse Residency Plano, TX"
    marks[fid] = {"status": "applied", "at": "x"}
    pages["https://jobs.example.org/search"] = page.replace("Posted 21 days ago", "").replace("Plano, TX", "Plano TX")
    checker.run(conn, settings, marks=marks, save_marks=False, fetcher=fetcher, now=t0.replace(hour=15), force=True)
    rows = conn.execute("SELECT id, active FROM findings").fetchall()
    assert len(rows) == 1 and rows[0]["active"] == 1
    assert marks == {rows[0]["id"]: {"status": "applied", "at": "x"}}
    assert conn.execute("SELECT COUNT(*) FROM events WHERE type='new_posting'").fetchone()[0] == 0
