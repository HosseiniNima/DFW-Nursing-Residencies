"""Pulls residency postings, cohort dates and open/closed wording out of HTML."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin

from bs4 import BeautifulSoup

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3, "apr": 4, "april": 4,
    "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7, "aug": 8, "august": 8, "sep": 9, "sept": 9,
    "september": 9, "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
# Month ranges (relative to the named year) that a season cohort could start in.
SEASONS = {"spring": (2, 5), "summer": (6, 8), "fall": (8, 11), "autumn": (8, 11), "winter": (0, 2)}

MONTH_RE = re.compile(
    r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|june?|july?|aug(?:ust)?|"
    r"sept?(?:ember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\.?\s+"
    r"(?:(\d{1,2})(?:st|nd|rd|th)?,?\s+)?(20\d{2})\b",
    re.I,
)
SEASON_RE = re.compile(r"\b(spring|summer|fall|autumn|winter)\s+(?:of\s+)?(20\d{2})\b", re.I)
SEASON_REV_RE = re.compile(r"\b(20\d{2})\s+(spring|summer|fall|autumn|winter)\b", re.I)
YEAR_COHORT_RE = re.compile(
    r"\b(20\d{2})\s+(?:cohort|residency|residents?|class|program)\b|"
    r"\b(?:cohort|class)\s+(?:of\s+)?(20\d{2})\b",
    re.I,
)

RESIDENCY_RE = re.compile(
    r"nurse\s+residen(?:cy|t)|\bresiden(?:cy|t)\b.*\b(?:rn|nurs\w*|gn|graduate)\b|"
    r"\b(?:rn|gn|graduate\s+nurse|new\s+grad(?:uate)?)\b.*\bresiden(?:cy|t)\b|"
    r"new\s+grad(?:uate)?\s+(?:rn|nurse)|graduate\s+nurse|\bgn\b|transition\s+to\s+practice|"
    r"\bstarn\b|bridge\s+program|\bpb-?rnr\b|post[- ]baccalaureate.*residency",
    re.I,
)
NOT_NURSING_RE = re.compile(
    r"pharmac|physician|\bmedical\s+resident|\bpgy|dental|dentist|psycholog|chaplain|crna|"
    r"anesthe|nurse\s+practitioner|\bnp\b|\baprn\b|fellowship|extern|\bintern(ship)?\b|"
    r"apprentice|\btech(nician)?\b|assistant|\bcna\b|\blvn\b|surgery\s+resident|radiolog|"
    r"therap(y|ist)|dietetic|\bpa\b",
    re.I,
)
CONTEXT_RE = re.compile(
    r"residen|cohort|new\s+grad|graduate\s+nurse|\bgn\b|apply|applica|start|program|class|"
    r"interview|deadline|\bopen",
    re.I,
)
OPEN_RE = re.compile(
    r"now\s+accepting|accepting\s+applications|applications?\s+(?:are\s+|is\s+)?(?:now\s+)?open\b|"
    r"apply\s+(?:now|today)|application\s+(?:window|period)\s+(?:is\s+)?(?:now\s+)?open|now\s+hiring",
    re.I,
)
CLOSED_RE = re.compile(
    r"applications?\s+(?:are\s+|is\s+)?(?:now\s+)?closed|not\s+(?:currently\s+)?accepting|"
    r"no\s+longer\s+accepting|application\s+(?:window|period)\s+(?:is\s+|has\s+)?closed",
    re.I,
)
# Link text that names a section of a site rather than an actual job opening.
NAV_RE = re.compile(
    r"\b(?:information|info|tracks?|opportunit\w*|learn|check\s+out|overview|faqs?|goals?|outcomes?|"
    r"structure|qualifications|benefits|faculty|about|click|view\s+all|see\s+all|positions)\b",
    re.I,
)
JOB_HREF_RE = re.compile(r"/jobs?/[^?#]*\d|/job/|job_?id=|requisition|/details?/|/posting/|jobdetail", re.I)
TITLE_SEPARATOR_RE = re.compile(r"\s[-–—|:]\s|[,(]|\s[-–—]|[-–—]\s")
JSON_TITLE_RE = re.compile(r'"(?:title|jobTitle|postingTitle|job_title|name)"\s*:\s*"((?:[^"\\]|\\.){6,200})"')


@dataclass
class Cohort:
    label: str
    start_min: int  # month index (year*12 + month-1)
    start_max: int


@dataclass
class Item:
    kind: str  # "posting" | "snippet"
    title: str
    url: str
    context: str = ""
    cohorts: list[Cohort] = field(default_factory=list)
    signal: str = ""  # "open" | "closed" | ""

    @property
    def key(self) -> str:
        norm = re.sub(r"[^a-z0-9]+", " ", self.title.lower()).strip()
        url = self.url if self.kind == "posting" else ""
        return hashlib.sha1(f"{self.kind}|{norm}|{url}".encode()).hexdigest()[:16]


@dataclass
class PageResult:
    text: str
    text_hash: str
    items: list[Item]
    page_signal: str


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "template"]):
        tag.decompose()
    lines = (_clean(line) for line in soup.get_text("\n").splitlines())
    return "\n".join(line for line in lines if line)


def find_cohorts(text: str, now_idx: int) -> list[Cohort]:
    """Every cohort/start date mentioned in `text`, ignoring years long past or far ahead."""
    found: dict[str, Cohort] = {}

    def add(label: str, lo: int, hi: int) -> None:
        if now_idx - 12 <= hi and lo <= now_idx + 48:
            found.setdefault(label.lower(), Cohort(label, lo, hi))

    taken: list[tuple[int, int]] = []  # spans already explained by a more specific date

    for m in MONTH_RE.finditer(text):
        idx = int(m.group(3)) * 12 + _month_key(m.group(1)) - 1
        add(_clean(m.group(0)), idx, idx)
        taken.append(m.span())
    for rx, season_group, year_group in ((SEASON_RE, 1, 2), (SEASON_REV_RE, 2, 1)):
        for m in rx.finditer(text):
            add(_clean(m.group(0)), *_season_range(m.group(season_group), int(m.group(year_group))))
            taken.append(m.span())
    for m in YEAR_COHORT_RE.finditer(text):
        # "October 2027 cohort" → the year-only reading of "2027 cohort" adds nothing
        year_start = m.start(1) if m.group(1) else m.start(2)
        if any(a <= year_start < b for a, b in taken):
            continue
        year = int(m.group(1) or m.group(2))
        add(_clean(m.group(0)), year * 12, year * 12 + 11)
    return list(found.values())


def _month_key(word: str) -> int:
    word = word.lower().rstrip(".")
    return MONTHS.get(word) or MONTHS[word[:3]]


def _season_range(season: str, year: int) -> tuple[int, int]:
    lo, hi = SEASONS[season.lower()]
    if season.lower() == "winter":  # "Winter 2025" cohorts start Dec 2024 – Feb 2025
        return year * 12 - 1, year * 12 + 1
    return year * 12 + lo, year * 12 + hi


def classify(cohorts: list[Cohort], target_from: int, target_until: int | None) -> str:
    """target / maybe / early / late / unknown — the best match among the dates mentioned."""
    if not cohorts:
        return "unknown"
    ranks = []
    for c in cohorts:
        hi_limit = target_until if target_until is not None else 10**9
        if c.start_min >= target_from and c.start_max <= hi_limit:
            ranks.append("target")
        elif c.start_max < target_from:
            ranks.append("early")
        elif c.start_min > hi_limit:
            ranks.append("late")
        else:
            ranks.append("maybe")
    for r in ("target", "maybe", "late", "early"):
        if r in ranks:
            return r
    return "unknown"


def signal_of(text: str) -> str:
    if CLOSED_RE.search(text):
        return "closed"
    if OPEN_RE.search(text):
        return "open"
    return ""


def is_residency_title(text: str) -> bool:
    return bool(RESIDENCY_RE.search(text)) and not NOT_NURSING_RE.search(text)


def looks_like_posting(title: str, href: str = "", now_idx: int = 0) -> bool:
    """Filters out menu links like "Nurse Residency Program" or "Program goals"."""
    if href and JOB_HREF_RE.search(href):
        return True
    if find_cohorts(title, now_idx or 2026 * 12):
        return True
    return bool(TITLE_SEPARATOR_RE.search(title)) and not NAV_RE.search(title)


def _postings(soup: BeautifulSoup, raw_html: str, base_url: str, now_idx: int) -> list[Item]:
    items: dict[str, Item] = {}
    for a in soup.find_all("a", href=True):
        title = _clean(a.get_text(" "))
        if not (6 <= len(title) <= 200) or not is_residency_title(title):
            continue
        href = a["href"].strip()
        if not looks_like_posting(title, href, now_idx):
            continue
        if href.startswith(("javascript:", "mailto:", "tel:")):
            href = ""
        url = urljoin(base_url, href) if href and not href.startswith("#") else base_url
        parent = a.find_parent(["li", "tr", "article", "section", "div"]) or a.parent
        context = _clean(parent.get_text(" "))[:400] if parent else title
        item = Item("posting", title, url, context)
        items.setdefault(item.key, item)

    # Many job boards ship their results as JSON inside the page.
    for m in JSON_TITLE_RE.finditer(raw_html):
        try:
            title = _clean(json.loads(f'"{m.group(1)}"'))
        except ValueError:
            title = _clean(m.group(1))
        if not is_residency_title(title) or "<" in title or not looks_like_posting(title, "", now_idx):
            continue
        window = raw_html[max(0, m.start() - 600): m.end() + 600]
        loc = re.search(r'"(?:city|location|cityState|primaryLocation|address)"\s*:\s*"([^"]{2,80})"', window)
        item = Item("posting", title, base_url, f"{title} {loc.group(1) if loc else ''}".strip())
        if not any(_clean(i.title).lower() == title.lower() for i in items.values()):
            items.setdefault(item.key, item)

    for item in items.values():
        item.cohorts = find_cohorts(item.title, now_idx) or find_cohorts(item.context, now_idx)
        item.signal = signal_of(item.context)
    return list(items.values())


def _snippets(text: str, base_url: str, now_idx: int) -> list[Item]:
    lines = text.splitlines()
    items: dict[str, Item] = {}
    for i, line in enumerate(lines):
        if len(line) > 500:
            parts = re.split(r"(?<=[.!?])\s+", line)
        else:
            parts = [line]
        for part in parts:
            cohorts = find_cohorts(part, now_idx)
            if not cohorts:
                continue
            around = " ".join(lines[max(0, i - 1): i + 2])
            if not CONTEXT_RE.search(part) and not CONTEXT_RE.search(around):
                continue
            snippet = part[:300]
            item = Item("snippet", snippet, base_url, around[:500], cohorts, signal_of(around))
            items.setdefault(item.key, item)
    return list(items.values())


def items_hash(items: list[Item]) -> str:
    return hashlib.sha1("\n".join(sorted(i.key for i in items)).encode()).hexdigest()[:16]


def analyze(html: str, base_url: str, kind: str, now_idx: int) -> PageResult:
    soup = BeautifulSoup(html, "html.parser")
    text = visible_text(html)
    if kind == "page":
        # Program pages: read the dates in the text; their links are just site navigation.
        items = _snippets(text, base_url, now_idx)
    else:
        items = _postings(soup, html, base_url, now_idx)
    # Hash only lines that look relevant so rotating banners/news don't count as changes.
    relevant = "\n".join(line for line in text.splitlines() if CONTEXT_RE.search(line) or MONTH_RE.search(line))
    text_hash = hashlib.sha1(relevant.encode()).hexdigest()[:16]
    return PageResult(text, text_hash, items, signal_of(text) if RESIDENCY_RE.search(text) else "")
