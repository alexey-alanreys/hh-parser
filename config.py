"""
HireScope — централизованная конфигурация.
Все константы, URL, заголовки и дефолты параметров находятся здесь.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"

STOPWORDS_FILE = DATA_DIR / "stopwords.txt"
SKILL_ALIASES_FILE = DATA_DIR / "skill_aliases.json"

# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

SEARCH_PER_PAGE = 50  # max supported by hh.ru

# data-qa selectors — stable across hh.ru redesigns
SELECTOR_VACANCY_TITLE_LINK = "[data-qa='serp-item__title']"
SELECTOR_VACANCY_TITLE_TEXT = "[data-qa='serp-item__title-text']"
SELECTOR_PAGER_NEXT = "[data-qa='pager-next']"
SELECTOR_DESCRIPTION = "[data-qa='vacancy-description']"
SELECTOR_SKILL = "[data-qa='skills-element']"

# ---------------------------------------------------------------------------
# Analysis defaults
# ---------------------------------------------------------------------------

DEFAULT_KEYWORD_THRESHOLD = 5
DEFAULT_SKILL_THRESHOLD = 5
DEFAULT_TOP_N = 30
DEFAULT_MIN_WORD_LENGTH = 3
DEFAULT_MAX_VACANCIES = 100
DEFAULT_REQUEST_DELAY = 1.0

# ---------------------------------------------------------------------------
# Experience filter values (hh.ru API)
# ---------------------------------------------------------------------------

EXPERIENCE_CHOICES = [
    "noExperience",
    "between1And3",
    "between3And6",
    "moreThan6",
]

# ---------------------------------------------------------------------------
# Region IDs (наиболее востребованные)
# ---------------------------------------------------------------------------

AREAS = {
    0: "Вся Россия",
    1: "Москва",
    2: "Санкт-Петербург",
    3: "Екатеринбург",
    4: "Новосибирск",
    88: "Казань",
}