"""Downloads pages, falling back to a headless browser for JavaScript-heavy sites."""

from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.parse import urlparse

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"
)
# Below this much visible text a page is probably an empty JavaScript shell.
MIN_USEFUL_TEXT = 400


@dataclass
class FetchResult:
    url: str
    final_url: str
    status: int | None
    html: str
    via: str  # "http" | "browser"
    error: str | None = None
    json: object = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.status is not None and self.status < 400 and bool(self.html)


class Fetcher:
    def __init__(self, timeout: float = 30, per_host_delay: float = 3, browser_fallback: bool = True):
        self.timeout = timeout
        self.per_host_delay = per_host_delay
        self.browser_fallback = browser_fallback
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9",
             "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8"}
        )
        self._last_hit: dict[str, float] = {}
        self._pw = None
        self._browser = None
        self._browser_failed = False

    def _wait_for_host(self, url: str) -> None:
        host = urlparse(url).netloc
        wait = self._last_hit.get(host, 0) + self.per_host_delay - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_hit[host] = time.monotonic()

    def get(self, url: str, render: str = "auto", visible_text_len=None) -> FetchResult:
        result = None
        if render != "always":
            result = self._http(url)
            looks_empty = result.ok and visible_text_len is not None and visible_text_len(result.html) < MIN_USEFUL_TEXT
            blocked = result.status in (401, 403, 406, 429, 503) or (result.error and result.status is None)
            if render == "never" or not self.browser_fallback or (result.ok and not looks_empty) or not (looks_empty or blocked):
                return result
        rendered = self._render(url)
        if rendered.ok or result is None:
            return rendered
        return result

    def _http(self, url: str) -> FetchResult:
        last_exc = None
        for attempt in range(2):
            self._wait_for_host(url)
            try:
                r = self.session.get(url, timeout=self.timeout, allow_redirects=True)
                err = None if r.status_code < 400 else f"HTTP {r.status_code}"
                return FetchResult(url, r.url, r.status_code, r.text, "http", err)
            except requests.RequestException as exc:
                last_exc = exc
                time.sleep(2 * (attempt + 1))
        return FetchResult(url, url, None, "", "http", f"{type(last_exc).__name__}: {last_exc}")

    def post_json(self, url: str, payload: dict) -> FetchResult:
        self._wait_for_host(url)
        try:
            r = self.session.post(url, json=payload, timeout=self.timeout,
                                  headers={"Accept": "application/json", "Content-Type": "application/json"})
            err = None if r.status_code < 400 else f"HTTP {r.status_code}"
            data = r.json() if err is None else None
            return FetchResult(url, r.url, r.status_code, r.text, "api", err, data)
        except (requests.RequestException, ValueError) as exc:
            return FetchResult(url, url, None, "", "api", f"{type(exc).__name__}: {exc}"[:300])

    def _render(self, url: str) -> FetchResult:
        if self._browser_failed:
            return FetchResult(url, url, None, "", "browser", "headless browser unavailable")
        try:
            if self._browser is None:
                from playwright.sync_api import sync_playwright

                self._pw = sync_playwright().start()
                self._browser = self._pw.chromium.launch(headless=True)
            self._wait_for_host(url)
            page = self._browser.new_page(user_agent=USER_AGENT)
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=self.timeout * 1000)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass  # some sites never go idle; take what has rendered
                status = resp.status if resp else None
                err = None if status is None or status < 400 else f"HTTP {status}"
                return FetchResult(url, page.url, status or 200, page.content(), "browser", err)
            finally:
                page.close()
        except ImportError:
            self._browser_failed = True
            return FetchResult(url, url, None, "", "browser", "playwright not installed")
        except Exception as exc:
            return FetchResult(url, url, None, "", "browser", f"{type(exc).__name__}: {exc}"[:300])

    def close(self) -> None:
        try:
            if self._browser:
                self._browser.close()
            if self._pw:
                self._pw.stop()
        except Exception:
            pass
