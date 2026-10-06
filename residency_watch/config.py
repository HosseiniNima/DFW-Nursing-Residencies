"""Loads config.yaml + hospitals.yaml and works out distance-based priorities."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass, field
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Tier:
    rank: int
    name: str
    max_miles: float
    check_every_hours: float


@dataclass
class Hospital:
    id: str
    name: str
    city: str
    lat: float
    lon: float
    system_id: str
    system_name: str
    match: list[str]
    distance_mi: float | None = None
    tier: Tier | None = None


@dataclass
class Source:
    id: str
    url: str
    kind: str  # "page" | "jobs" | "workday"
    system_id: str
    system_name: str
    render: str = "auto"  # "auto" | "always" | "never"
    verified: bool = True
    search: list[str] = field(default_factory=list)  # workday search terms
    dfw_only: bool = False  # drop postings that don't name a DFW hospital or city
    hospitals: list[Hospital] = field(default_factory=list)  # empty => aggregator
    tier: Tier | None = None
    distance_mi: float | None = None  # closest hospital this source covers


@dataclass
class System:
    id: str
    name: str
    aliases: list[str]
    hospitals: list[Hospital]
    sources: list[Source]


@dataclass
class Settings:
    home: tuple[float, float] | None
    home_label: str
    target_from: int  # month index: year * 12 + (month - 1)
    target_until: int | None
    tiers: list[Tier]
    favorites: set[str]
    issue_levels: set[str]
    timeout: float
    per_host_delay: float
    browser_fallback: bool
    keep_check_history_days: int
    systems: list[System]

    @property
    def hospitals(self) -> list[Hospital]:
        return [h for s in self.systems for h in s.hospitals]

    @property
    def sources(self) -> list[Source]:
        return [src for s in self.systems for src in s.sources]


def month_index(text: str) -> int:
    year, month = (int(p) for p in text.strip().split("-")[:2])
    return year * 12 + (month - 1)


def month_label(idx: int) -> str:
    import calendar

    return f"{calendar.month_name[idx % 12 + 1]} {idx // 12}"


def haversine_miles(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def geocode_zip(zip_code: str, timeout: float = 15) -> tuple[float, float] | None:
    try:
        r = requests.get(f"https://api.zippopotam.us/us/{zip_code.strip()}", timeout=timeout)
        r.raise_for_status()
        place = r.json()["places"][0]
        return float(place["latitude"]), float(place["longitude"])
    except Exception as exc:  # network trouble shouldn't stop the run
        print(f"[warn] could not look up ZIP {zip_code}: {exc}")
        return None


def resolve_home(cfg: dict) -> tuple[tuple[float, float] | None, str]:
    home = cfg.get("home") or {}
    lat = os.environ.get("HOME_LAT") or home.get("lat")
    lon = os.environ.get("HOME_LON") or home.get("lon")
    if lat not in (None, "") and lon not in (None, ""):
        return (float(lat), float(lon)), "coordinates"
    zip_code = os.environ.get("HOME_ZIP") or str(home.get("zip") or "")
    if zip_code.strip():
        coords = geocode_zip(zip_code)
        if coords:
            return coords, f"ZIP {zip_code.strip()}"
    return None, "not set"


def load(config_path: Path | None = None, hospitals_path: Path | None = None) -> Settings:
    cfg = yaml.safe_load((config_path or ROOT / "config.yaml").read_text()) or {}
    hosp = yaml.safe_load((hospitals_path or ROOT / "hospitals.yaml").read_text()) or {}

    tiers = [
        Tier(i, t["name"], float(t["max_miles"]), float(t["check_every_hours"]))
        for i, t in enumerate(cfg.get("priority_tiers") or [])
    ] or [Tier(0, "All", 9999, 24)]
    home, home_label = resolve_home(cfg)
    favorites = set(cfg.get("favorites") or [])

    def tier_for(hospital_id: str, miles: float | None) -> Tier:
        if hospital_id in favorites:
            return tiers[0]
        if miles is None:  # no home set: everything gets the slowest (daily) tier
            return tiers[-1]
        return next((t for t in tiers if miles <= t.max_miles), tiers[-1])

    systems = []
    for s in hosp.get("systems") or []:
        hospitals = []
        for h in s.get("hospitals") or []:
            dist = haversine_miles(home, (h["lat"], h["lon"])) if home else None
            hospitals.append(
                Hospital(
                    id=h["id"], name=h["name"], city=h["city"], lat=h["lat"], lon=h["lon"],
                    system_id=s["id"], system_name=s["name"],
                    match=list(h.get("match") or [h["city"]]),
                    distance_mi=dist, tier=tier_for(h["id"], dist),
                )
            )
        sources = []
        for src in s.get("sources") or []:
            sources.append(
                Source(
                    id=src["id"], url=src["url"], kind=src.get("kind", "page"),
                    system_id=s["id"], system_name=s["name"],
                    render=src.get("render", "auto"), verified=src.get("verified", True),
                    search=list(src.get("search") or ["nurse residency", "new grad"]),
                    dfw_only=bool(src.get("dfw_only", False)),
                    hospitals=hospitals,
                )
            )
        systems.append(System(s["id"], s["name"], list(s.get("aliases") or [s["name"]]), hospitals, sources))

    all_hospitals = [h for s in systems for h in s.hospitals]
    for system in systems:
        covered = system.hospitals or all_hospitals  # aggregators cover everyone
        best = min(covered, key=lambda h: (h.tier.rank, h.distance_mi if h.distance_mi is not None else 1e9))
        for src in system.sources:
            src.tier = best.tier
            src.distance_mi = best.distance_mi

    until = str(cfg.get("target_until") or "").strip()
    alerts = cfg.get("alerts") or {}
    fetch = cfg.get("fetch") or {}
    return Settings(
        home=home,
        home_label=home_label,
        target_from=month_index(str(cfg.get("target_from", "2027-08"))),
        target_until=month_index(until) if until else None,
        tiers=tiers,
        favorites=favorites,
        issue_levels=set(alerts.get("issue_levels") or ["high", "medium"]),
        timeout=float(fetch.get("timeout_seconds", 30)),
        per_host_delay=float(fetch.get("per_host_delay_seconds", 3)),
        browser_fallback=bool(fetch.get("browser_fallback", True)),
        keep_check_history_days=int(cfg.get("keep_check_history_days", 30)),
        systems=systems,
    )
