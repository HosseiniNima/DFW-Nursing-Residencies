"""Searches Workday career sites through the JSON API their own search page uses."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from . import extract
from .fetch import FetchResult, Fetcher

# https://acme.wd5.myworkdayjobs.com/en-US/External        → tenant acme, site External
# https://wd12.myworkdaysite.com/en-US/recruiting/acme/Jobs → tenant acme, site Jobs
JOBS_RE = re.compile(r"^(?P<tenant>[^.]+)\.wd\d+\.myworkdayjobs\.com$")
SITE_PATH_RE = re.compile(r"^/(?:[a-z]{2}-[A-Z]{2}/)?(?:recruiting/(?P<tenant>[^/]+)/)?(?P<site>[^/?#]+)")
PAGE_SIZE = 20


def is_workday(url: str) -> bool:
    host = urlparse(url).netloc
    return host.endswith(".myworkdayjobs.com") or host.endswith(".myworkdaysite.com")


def api_url(site_url: str) -> tuple[str, str]:
    """(jobs API endpoint, public base URL that job paths hang off)."""
    u = urlparse(site_url)
    m = SITE_PATH_RE.match(u.path)
    if not m:
        raise ValueError(f"not a Workday career site URL: {site_url}")
    host_match = JOBS_RE.match(u.netloc)
    tenant = m.group("tenant") or (host_match.group("tenant") if host_match else None)
    if not tenant:
        raise ValueError(f"can't tell the Workday tenant from {site_url}")
    site = m.group("site")
    base = f"{u.scheme}://{u.netloc}" + u.path[: m.end()]
    return f"{u.scheme}://{u.netloc}/wday/cxs/{tenant}/{site}/jobs", base


def search(fetcher: Fetcher, site_url: str, terms: list[str], now_idx: int, max_pages: int = 3
           ) -> tuple[FetchResult, list[extract.Item]]:
    endpoint, base = api_url(site_url)
    items: dict[str, extract.Item] = {}
    last = None
    for term in terms:
        for page in range(max_pages):
            last = fetcher.post_json(endpoint, {"appliedFacets": {}, "limit": PAGE_SIZE,
                                                "offset": page * PAGE_SIZE, "searchText": term})
            if not last.ok:
                return last, []
            data = last.json or {}
            postings = data.get("jobPostings") or []
            for p in postings:
                title = (p.get("title") or "").strip()
                if not extract.is_residency_title(title):
                    continue
                context = " ".join(str(p.get(k) or "") for k in ("title", "locationsText", "postedOn"))
                item = extract.Item("posting", title, base + (p.get("externalPath") or ""), context)
                item.cohorts = extract.find_cohorts(title, now_idx)
                items.setdefault(item.key, item)
            if (page + 1) * PAGE_SIZE >= (data.get("total") or 0) or not postings:
                break
    return last, list(items.values())
