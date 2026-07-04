"""HTTP client with rate limiting and a disk cache."""

import logging
import re
import time
from pathlib import Path

import requests

from app.config import REQUEST_HEADERS, REQUEST_TIMEOUT

log = logging.getLogger("hhparser.fetcher")


class Fetcher:
    def __init__(self, delay: float, cache_dir: Path | None) -> None:
        self.delay = delay
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

    def get(self, url: str, params: dict | None = None) -> str:
        cache_key = url + str(sorted(params.items()) if params else "")
        cache_path = self._cache_path(cache_key)

        if cache_path and cache_path.exists():
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
