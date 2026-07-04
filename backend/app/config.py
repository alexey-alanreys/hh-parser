"""hhParser backend configuration.

Analysis thresholds and the lemmatize/bigrams flags are intentionally
hardcoded here instead of being exposed via the API/UI.
"""

from pathlib import Path

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"

STOPWORDS_FILE = DATA_DIR / "stopwords.txt"
SKILL_ALIASES_FILE = DATA_DIR / "skill_aliases.json"

CACHE_DIR = Path("/tmp/hhparser-cache")  # ephemeral, not persisted across restarts

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

SKILL_THRESHOLD = 5
KEYWORD_THRESHOLD = 5
MIN_WORD_LENGTH = 3
TOP_N = 30
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
