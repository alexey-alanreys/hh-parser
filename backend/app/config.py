"""hhParser backend configuration.

Analysis thresholds and the lemmatize/bigrams flags are intentionally
hardcoded here instead of being exposed via the API/UI.
"""

from pathlib import Path

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"

STOPWORDS_FILE = DATA_DIR / "stopwords.txt"
SKILL_ALIASES_FILE = DATA_DIR / "skill_aliases.json"

CACHE_DIR = APP_DIR.parent / ".cache"  # backend/.cache — gitignored, not persisted in Docker unless mounted
CACHE_TTL_HOURS = 24  # stale entries are skipped on read and swept on process start

SEARCH_URL = "https://hh.ru/search/vacancy"
VACANCY_URL = "https://hh.ru/vacancy"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

REQUEST_TIMEOUT = 15  # seconds
REQUEST_DELAY = 1.0  # seconds between requests, rate-limit protection

SEARCH_PER_PAGE = 50  # hh.ru max page size

SELECTOR_VACANCY_TITLE_LINK = "[data-qa='serp-item__title']"
SELECTOR_VACANCY_TITLE_TEXT = "[data-qa='serp-item__title-text']"
SELECTOR_PAGER_PAGE = "[data-qa='pager-page']"
SELECTOR_PAGER_CURRENT = "[data-qa='pager-page'][aria-current='true']"
SELECTOR_DESCRIPTION = "[data-qa='vacancy-description']"
SELECTOR_SKILL = "[data-qa='skills-element']"

SKILL_THRESHOLD_RATIO = 0.06  # a skill must appear in at least this share of scanned vacancies
KEYWORD_THRESHOLD_RATIO = 0.04
MIN_THRESHOLD_COUNT = 2  # floor, avoids single-vacancy noise on small scans

TOP_N_SKILLS = 30  # matches hh.ru's own per-vacancy tag limit
TOP_N_KEYWORDS = 50
MIN_WORD_LENGTH = 3
USE_BIGRAMS = True
LEMMATIZE = True

AREA_RUSSIA = 0

EXPERIENCE_CHOICES = [
    "noExperience",
    "between1And3",
    "between3And6",
    "moreThan6",
]

MAX_VACANCIES_LIMIT = 500  # guards against accidental high load on hh.ru