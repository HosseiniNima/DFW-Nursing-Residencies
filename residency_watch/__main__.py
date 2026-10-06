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
    sub.add_parser("hospitals", help="list hospitals by distance and check frequency")

    args = p.parse_args(argv)
    settings = config.load()

    if args.cmd == "hospitals":
        for h in sorted(settings.hospitals, key=lambda h: (h.tier.rank, h.distance_mi or 0)):
            dist = f"{h.distance_mi:5.1f} mi" if h.distance_mi is not None else "   ?   "
            print(f"{dist}  {h.tier.name:<12} {h.name}")
        print(f"\nHome: {settings.home_label}")
        return 0

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


if __name__ == "__main__":
    sys.exit(main())
