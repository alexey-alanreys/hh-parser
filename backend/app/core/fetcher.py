"""HTTP client with rate limiting and a disk cache."""

import logging
import re
import time
from pathlib import Path

import requests

from app.config import REQUEST_HEADERS, REQUEST_TIMEOUT

log = logging.getLogger("hhparser.fetcher")


class Fetcher:
    def __init__(self, delay: float, cache_dir: Path | None, ttl_hours: float) -> None:
        self.delay = delay
        self.ttl_seconds = ttl_hours * 3600
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        self.cache_dir = cache_dir
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, key: str) -> Path | None:
        if not self.cache_dir:
            return None
        safe = re.sub(r"[^\w]", "_", key)[:180]
        return self.cache_dir / f"{safe}.html"

    def _is_fresh(self, path: Path) -> bool:
        age_seconds = time.time() - path.stat().st_mtime
        return age_seconds < self.ttl_seconds

    def get(self, url: str, params: dict | None = None) -> str:
        cache_key = url + str(sorted(params.items()) if params else "")
        cache_path = self._cache_path(cache_key)

        if cache_path and cache_path.exists() and self._is_fresh(cache_path):
            log.debug("Cache hit: %s", url)
            return cache_path.read_text(encoding="utf-8")

        time.sleep(self.delay)
        log.debug("GET %s params=%s", url, params)

        resp = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        html = resp.text

        if cache_path:
            cache_path.write_text(html, encoding="utf-8")

        return html


def sweep_stale_cache(cache_dir: Path, ttl_hours: float) -> int:
    """Deletes cache files older than ttl_hours. Returns the number removed.

    Intended to run once on process startup (see app/main.py lifespan) so the
    cache self-cleans without a scheduled task or manual flag. This does not
    catch entries that are never re-requested during a long-lived process —
    those are only swept on the next restart.
    """
    if not cache_dir.exists():
        return 0

    cutoff = time.time() - ttl_hours * 3600
    removed = 0
    for path in cache_dir.glob("*.html"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError as e:
            log.warning("Could not sweep cache file %s: %s", path, e)
    return removed