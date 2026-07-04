"""Scraping and analysis pipeline: collect -> enrich -> analyze."""

from __future__ import annotations

import logging
from typing import Callable

from app.config import (
    AREA_RUSSIA,
    CACHE_DIR,
    KEYWORD_THRESHOLD,
    LEMMATIZE,
    MIN_WORD_LENGTH,
    REQUEST_DELAY,
    SEARCH_PER_PAGE,
    SEARCH_URL,
    SKILL_THRESHOLD,
    USE_BIGRAMS,
)
from app.core import Analyzer, Fetcher, Parser, load_skill_aliases, load_stopwords
from app.models import AnalysisResult, Vacancy
from app.schemas import JobStage, ScanRequest

log = logging.getLogger("hhparser.pipeline")

ProgressCallback = Callable[[JobStage, int, int], None]


class NoVacanciesFoundError(Exception):
    """No vacancies matched the query."""


def _collect_vacancies(
    fetcher: Fetcher,
    parser: Parser,
    query: str,
    max_vacancies: int,
    experience: str | None,
    on_progress: ProgressCallback,
) -> list[Vacancy]:
    vacancies: list[Vacancy] = []
    page = 0

    while len(vacancies) < max_vacancies:
        params: dict = {
            "text": query,
            "area": AREA_RUSSIA,
            "per_page": SEARCH_PER_PAGE,
            "page": page,
        }
        if experience:
            params["experience"] = experience

        on_progress(JobStage.COLLECTING, len(vacancies), max_vacancies)
        html = fetcher.get(SEARCH_URL, params=params)
        items = parser.parse_search_page(html)

        if not items:
            log.info("Страница %d пуста — останавливаемся", page + 1)
            break

        for item in items:
            if len(vacancies) >= max_vacancies:
                break
            vacancies.append(Vacancy(id=item["id"], title=item["title"], url=item["url"]))

        if not parser.has_next_page(html):
            break

        page += 1

    return vacancies


def _enrich_vacancies(
    fetcher: Fetcher,
    parser: Parser,
    vacancies: list[Vacancy],
    on_progress: ProgressCallback,
) -> list[Vacancy]:
    total = len(vacancies)
    for i, vacancy in enumerate(vacancies, 1):
        on_progress(JobStage.ENRICHING, i, total)
        try:
            html = fetcher.get(vacancy.url)
            desc, skills = parser.parse_vacancy_page(html)
            vacancy.description_text = desc
            vacancy.skills = skills
        except Exception as e:
            log.warning("Ошибка при загрузке %s: %s", vacancy.url, e)
    return vacancies


def run_pipeline(request: ScanRequest, on_progress: ProgressCallback) -> AnalysisResult:
    """Blocking call — run in a separate thread (see app/jobs.py)."""
    stopwords = load_stopwords()
    skill_aliases = load_skill_aliases()

    fetcher = Fetcher(delay=REQUEST_DELAY, cache_dir=CACHE_DIR)
    parser = Parser()
    analyzer = Analyzer(
        stopwords=stopwords,
        skill_aliases=skill_aliases,
        min_word_length=MIN_WORD_LENGTH,
        use_bigrams=USE_BIGRAMS,
        lemmatize=LEMMATIZE,
    )

    vacancies = _collect_vacancies(
        fetcher, parser, request.query, request.max_vacancies, request.experience, on_progress
    )
    if not vacancies:
        raise NoVacanciesFoundError("Вакансии не найдены — проверьте запрос")

    vacancies = _enrich_vacancies(fetcher, parser, vacancies, on_progress)

    on_progress(JobStage.ANALYZING, 0, 1)
    keyword_counter = analyzer.count_keywords(vacancies)
    skill_counter = analyzer.count_skills(vacancies)

    all_keywords = keyword_counter.most_common()
    all_skills = skill_counter.most_common()

    hot_keywords = [(w, c) for w, c in all_keywords if c >= KEYWORD_THRESHOLD]
    hot_skills = [(s, c) for s, c in all_skills if c >= SKILL_THRESHOLD]
    on_progress(JobStage.ANALYZING, 1, 1)

    return AnalysisResult(
        query=request.query,
        total_vacancies=len(vacancies),
        hot_keywords=hot_keywords,
        hot_skills=hot_skills,
        all_keywords=all_keywords,
        all_skills=all_skills,
    )
