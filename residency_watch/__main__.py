"""Command line: python -m residency_watch [run|report|hospitals]"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import checker, config, db, report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="residency_watch", description="Track DFW nurse residency openings.")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="check the sources that are due, then rebuild REPORT.md")
    run.add_argument("--force", action="store_true", help="check every source now, ignoring the schedule")
    run.add_argument("--only", nargs="+", help="only these source or system ids (e.g. thr bsw-search-residency)")
    run.add_argument("--alerts-out", type=Path, help="write a GitHub issue title/body here if there are new alerts")

    sub.add_parser("report", help="rebuild REPORT.md without checking anything")
    probe = sub.add_parser("probe", help="fetch URLs or source ids and show what would be found (for fixing hospitals.yaml)")
    probe.add_argument("urls", nargs="+", help="URLs, or source ids from hospitals.yaml")
    probe.add_argument("--kind", default="jobs", choices=["jobs", "page"])
    sub.add_parser("hospitals", help="list hospitals by distance and check frequency")

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

    conn = db.open_db()
    if args.cmd == "run":
        checker.run(conn, settings, force=args.force, only=set(args.only) if args.only else None)
        if args.alerts_out:
            alert = report.pending_alerts(conn, settings)
            args.alerts_out.unlink(missing_ok=True)
            if alert:
                title, body = alert
                args.alerts_out.write_text(title + "\n" + body)
                print(f"ALERT: {title}")
            gh_out = os.environ.get("GITHUB_OUTPUT")
            if gh_out:
                with open(gh_out, "a") as fh:
                    fh.write(f"has_alerts={'true' if alert else 'false'}\n")
    (config.ROOT / "REPORT.md").write_text(report.build_report(conn, settings))
    db.save_db(conn)
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
