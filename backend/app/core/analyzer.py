"""Keyword and skill frequency analysis."""

import json
import logging
import re
import unicodedata
from collections import Counter

from app.config import SKILL_ALIASES_FILE, STOPWORDS_FILE
from app.models import Vacancy

log = logging.getLogger("hhparser.analyzer")

IGNORE_MARKER = "_ignore"


def _normalize_whitespace(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def load_stopwords() -> set[str]:
    words: set[str] = set()
    if STOPWORDS_FILE.exists():
        for line in STOPWORDS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                words.add(line.lower())
        log.debug("Загружено %d стоп-слов из %s", len(words), STOPWORDS_FILE)
    else:
        log.warning("Файл стоп-слов не найден: %s", STOPWORDS_FILE)
    return words


def load_skill_aliases() -> dict[str, str]:
    if not SKILL_ALIASES_FILE.exists():
        log.warning("Файл алиасов навыков не найден: %s", SKILL_ALIASES_FILE)
        return {}

    raw: dict = json.loads(SKILL_ALIASES_FILE.read_text(encoding="utf-8"))
    return {k.lower(): v for k, v in raw.items() if not k.startswith("_")}


def _try_load_morph():
    """Loads pymorphy3 if available; lemmatization is disabled silently otherwise."""
    try:
        import pymorphy3
        morph = pymorphy3.MorphAnalyzer()
        log.debug("pymorphy3 загружен — лемматизация включена")
        return morph
    except ImportError:
        log.warning(
            "pymorphy3 не установлен — лемматизация отключена. "
            "Установите: pip install pymorphy3 pymorphy3-dicts-ru"
        )
        return None


class Analyzer:
    def __init__(
        self,
        stopwords: set[str],
        skill_aliases: dict[str, str],
        min_word_length: int,
        use_bigrams: bool,
        lemmatize: bool,
    ) -> None:
        self.stopwords = stopwords
        self.skill_aliases = skill_aliases
        self.min_word_length = min_word_length
        self.use_bigrams = use_bigrams
        self.morph = _try_load_morph() if lemmatize else None

    def _lemmatize(self, word: str) -> str:
        if self.morph is None:
            return word
        if re.match(r"^[a-z]", word):
            return word
        return self.morph.parse(word)[0].normal_form

    def _normalize_skill(self, skill: str) -> str | None:
        normalized = _normalize_whitespace(skill)
        key = normalized.lower()
        resolved = self.skill_aliases.get(key, normalized.title())
        if resolved == IGNORE_MARKER:
            return None
        return resolved

    def _tokenize(self, text: str) -> list[str]:
        pattern = rf"[а-яёa-z][а-яёa-z\-]{{{self.min_word_length - 1},}}"
        words = re.findall(pattern, text.lower())
        tokens = []
        for word in words:
            if word in self.stopwords:
                continue
            lemma = self._lemmatize(word)
            if lemma in self.stopwords:
                continue
            tokens.append(lemma)
        return tokens

    def _bigrams(self, tokens: list[str]) -> list[str]:
        # Adjacent duplicate lemmas (section header repeating a word from the
        # following text, OCR-like artifacts in hh.ru markup) produce
        # meaningless "X X" bigrams — filter them out.
        return [
            f"{tokens[i]} {tokens[i + 1]}"
            for i in range(len(tokens) - 1)
            if tokens[i] != tokens[i + 1]
        ]

    def count_keywords(self, vacancies: list[Vacancy]) -> Counter:
        counter: Counter = Counter()
        for v in vacancies:
            tokens = self._tokenize(v.description_text)
            counter.update(tokens)
            if self.use_bigrams:
                counter.update(self._bigrams(tokens))
        return counter

    def count_skills(self, vacancies: list[Vacancy]) -> Counter:
        counter: Counter = Counter()
        for v in vacancies:
            normalized = [
                result
                for s in v.skills
                if s.strip()
                for result in (self._normalize_skill(s),)
                if result is not None
            ]
            counter.update(normalized)
        return counter