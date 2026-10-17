"""Command line: python -m residency_watch [run|report|hospitals]"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from . import checker, config, db, marks as marks_mod, report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="residency_watch", description="Track DFW nurse residency openings.")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="check the sources that are due, then rebuild REPORT.md")
    run.add_argument("--force", action="store_true", help="check every source now, ignoring the schedule")
    run.add_argument("--only", nargs="+", help="only these source or system ids (e.g. thr bsw-search-residency)")
    run.add_argument("--alerts-out", type=Path, help="write new alerts here as JSON (one GitHub issue per posting)")

    sub.add_parser("report", help="rebuild REPORT.md without checking anything")
    probe = sub.add_parser("probe", help="fetch URLs or source ids and show what would be found (for fixing hospitals.yaml)")
    probe.add_argument("urls", nargs="+", help="URLs, or source ids from hospitals.yaml")
    probe.add_argument("--kind", default="jobs", choices=["jobs", "page"])
    sub.add_parser("hospitals", help="list hospitals by distance and check frequency")

    mark = sub.add_parser("mark", help="mark a posting as opened / applied / skip (not interested), or clear it")
    mark.add_argument("ref", help="the Code from REPORT.md (e.g. 3fa9c2), or an alert issue number (e.g. #12)")
    mark.add_argument("status", choices=[*marks_mod.STATUSES, "clear"])
    mark.add_argument("--note", help="optional note, e.g. 'interview 3/14'")

    sub.add_parser("sync-issue", help="(GitHub Actions) record the mark implied by an alert issue's labels; "
                                      "reads ISSUE_NUMBER, ISSUE_STATE, ISSUE_LABELS, ISSUE_BODY")
    link = sub.add_parser("link", help="(GitHub Actions) remember which issue was opened for a posting")
    link.add_argument("finding_id")
    link.add_argument("issue", type=int)

    args = p.parse_args(argv)
    settings = config.load()

    if args.cmd == "hospitals":
        for h in sorted(settings.hospitals, key=lambda h: (h.tier.rank, h.distance_mi or 0)):
            dist = f"{h.distance_mi:5.1f} mi" if h.distance_mi is not None else "   ?   "
            print(f"{dist}  {h.tier.name:<12} {h.name}")
        print(f"\nHome: {settings.home_label}")
        return 0

    if args.cmd == "probe":
        return _probe(settings, args.urls, args.kind)

    if args.cmd == "sync-issue":
        return _sync_issue(settings)

    conn = db.open_db()
    if args.cmd == "mark":
        return _mark(conn, settings, args.ref, args.status, args.note)
    if args.cmd == "link":
        conn.execute("UPDATE findings SET issue_number = ? WHERE id = ?", (args.issue, args.finding_id))
        db.save_db(conn)
        return 0
    if args.cmd == "run":
        checker.run(conn, settings, force=args.force, only=set(args.only) if args.only else None)
        if args.alerts_out:
            alerts = report.pending_alerts(conn, settings)
            args.alerts_out.write_text(json.dumps(alerts, indent=2, ensure_ascii=False))
            for a in alerts:
                print(f"ALERT: {a['title'] or 'update on issue #' + str(a['issue'])}")
            gh_out = os.environ.get("GITHUB_OUTPUT")
            if gh_out:
                with open(gh_out, "a") as fh:
                    fh.write(f"has_alerts={'true' if alerts else 'false'}\n")
    (config.ROOT / "REPORT.md").write_text(report.build_report(conn, settings))
    db.save_db(conn)
    return 0


def _mark(conn, settings: config.Settings, ref: str, status: str, note: str | None) -> int:
    try:
        fid = marks_mod.resolve(conn, ref)
    except LookupError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    marks = marks_mod.load()
    row = conn.execute("SELECT title, issue_number FROM findings WHERE id = ?", (fid,)).fetchone()
    marks_mod.set_status(marks, fid, None if status == "clear" else status, checker.iso(checker.utcnow()),
                         note=note, issue=row["issue_number"])
    marks_mod.save(marks)
    (config.ROOT / "REPORT.md").write_text(report.build_report(conn, settings, marks))
    print(f"{row['title']}: {marks_mod.STATUSES.get(status, 'cleared')}")
    return 0


def _sync_issue(settings: config.Settings) -> int:
    fid = marks_mod.finding_from_issue_body(os.environ.get("ISSUE_BODY", ""))
    if not fid:
        print("This issue isn't tied to a single posting; nothing to record.")
        return 0
    labels = [x for x in os.environ.get("ISSUE_LABELS", "").split(",") if x]
    status = marks_mod.status_from_issue(labels, os.environ.get("ISSUE_STATE", "open"))
    number = int(os.environ.get("ISSUE_NUMBER") or 0) or None
    marks = marks_mod.load()
    if not marks_mod.set_status(marks, fid, status, checker.iso(checker.utcnow()), issue=number):
        print("No change.")
        return 0
    marks_mod.save(marks)
    conn = db.open_db(db_path=None)  # read-only use: don't touch the committed dump
    (config.ROOT / "REPORT.md").write_text(report.build_report(conn, settings, marks))
    print(f"{fid}: {marks_mod.STATUSES.get(status or '', 'cleared')}")
    return 0


def _probe(settings: config.Settings, urls: list[str], kind: str) -> int:
    import re

    from bs4 import BeautifulSoup

    from . import extract, workday
    from .checker import utcnow
    from .fetch import Fetcher

    now = utcnow()
    now_idx = now.year * 12 + now.month - 1
    sources = {s.id: s for s in settings.sources}
    fetcher = Fetcher(settings.timeout, 1, settings.browser_fallback)
    try:
        for target in urls:
            src = sources.get(target)
            url, src_kind = (src.url, src.kind) if src else (target, "workday" if workday.is_workday(target) else kind)
            if src_kind == "workday":
                res, items = workday.search(fetcher, url, src.search if src else ["nurse residency"], now_idx)
            else:
                res = fetcher.get(url, src.render if src else "auto", visible_text_len=lambda html: len(extract.visible_text(html)))
            print(f"\n=== {target}\n  status={res.status} via={res.via} error={res.error}\n  final={res.final_url}")
            if not res.ok:
                continue
            if src_kind == "workday":
                total = (res.json or {}).get("total")
                print(f"  workday total={total} residency_items={len(items)}")
                for item in items[:25]:
                    print(f"  - {item.context[:160]} | {item.url[:150]}")
                continue
            soup = BeautifulSoup(res.html, "html.parser")
            title = soup.title.get_text(strip=True) if soup.title else ""
            page = extract.analyze(res.html, res.final_url, src_kind, now_idx)
            print(f"  title={title!r} text_len={len(page.text)} items={len(page.items)} signal={page.page_signal!r}")
            for item in page.items[:25]:
                cohort = ", ".join(c.label for c in item.cohorts)
                print(f"  - [{item.kind}] {item.title[:120]} | {cohort} | {item.url[:150]}")
            links = sorted({a["href"] for a in soup.find_all("a", href=True)
                            if re.search(r"search|job|career|residen|grad", a["href"], re.I)})
            print(f"  candidate links ({len(links)}):")
            for href in links[:40]:
                print(f"    {href[:200]}")
    finally:
        fetcher.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
