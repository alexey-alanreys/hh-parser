"""
HireScope — частотный анализ ключевых слов и навыков.
"""

import json
import logging
import re
from collections import Counter
from pathlib import Path
from typing import Optional

from config import SKILL_ALIASES_FILE, STOPWORDS_FILE
from models import Vacancy

log = logging.getLogger("hirescope.analyzer")

IGNORE_MARKER = "_ignore"


def load_stopwords(extra_file: Optional[str] = None) -> set[str]:
    """
    Загружает стоп-слова из data/stopwords.txt.
    Строки начинающиеся с # считаются комментариями и игнорируются.
    Опционально добавляет слова из пользовательского файла.
    """
    words: set[str] = set()

    if STOPWORDS_FILE.exists():
        for line in STOPWORDS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                words.add(line.lower())
        log.debug("Загружено %d стоп-слов из %s", len(words), STOPWORDS_FILE)
    else:
        log.warning("Файл стоп-слов не найден: %s", STOPWORDS_FILE)

    if extra_file:
        path = Path(extra_file)
        if path.exists():
            extra = {
                line.strip().lower()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip() and not line.startswith("#")
            }
            words |= extra
            log.debug("Добавлено %d стоп-слов из %s", len(extra), extra_file)
        else:
            log.warning("Пользовательский файл стоп-слов не найден: %s", extra_file)

    return words


def load_skill_aliases() -> dict[str, str]:
    """
    Загружает словарь нормализации навыков из data/skill_aliases.json.
    Ключи хранятся в lowercase для регистронезависимого сравнения.
    Значение "_ignore" означает что навык нужно пропустить.
    """
    if not SKILL_ALIASES_FILE.exists():
        log.warning("Файл алиасов навыков не найден: %s", SKILL_ALIASES_FILE)
        return {}

    raw: dict = json.loads(SKILL_ALIASES_FILE.read_text(encoding="utf-8"))
    return {
        k.lower(): v
        for k, v in raw.items()
        if not k.startswith("_")  # пропускаем служебные ключи типа _comment
    }


class Analyzer:
    def __init__(
        self,
        stopwords: set[str],
        skill_aliases: dict[str, str],
        min_word_length: int = 3,
        use_bigrams: bool = False,
    ) -> None:
        self.stopwords = stopwords
        self.skill_aliases = skill_aliases
        self.min_word_length = min_word_length
        self.use_bigrams = use_bigrams

    def _normalize_skill(self, skill: str) -> Optional[str]:
        """
        Приводит навык к каноническому виду через таблицу алиасов.
        Возвращает None если навык помечен как _ignore.
        Если алиас не найден — возвращает навык с заглавной буквы.
        """
        key = skill.strip().lower()
        resolved = self.skill_aliases.get(key, skill.strip().title())
        if resolved == IGNORE_MARKER:
            return None
        return resolved

    def _tokenize(self, text: str) -> list[str]:
        pattern = rf"[а-яёa-z][а-яёa-z\-]{{{self.min_word_length - 1},}}"
        words = re.findall(pattern, text.lower())
        return [w for w in words if w not in self.stopwords]

    def _bigrams(self, tokens: list[str]) -> list[str]:
        return [f"{tokens[i]} {tokens[i + 1]}" for i in range(len(tokens) - 1)]

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