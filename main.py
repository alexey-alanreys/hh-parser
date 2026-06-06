"""
HireScope — точка входа.
Содержит CLI и основной pipeline: сбор → обогащение → анализ → отчёт.
"""

from __future__ import annotations

import argparse
import logging
import sys

from config import (
    DEFAULT_KEYWORD_THRESHOLD,
    DEFAULT_MAX_VACANCIES,
    DEFAULT_MIN_WORD_LENGTH,
    DEFAULT_REQUEST_DELAY,
    DEFAULT_SKILL_THRESHOLD,
    DEFAULT_TOP_N,
    EXPERIENCE_CHOICES,
    SEARCH_PER_PAGE,
    SEARCH_URL,
)
from core import (
    Analyzer,
    Fetcher,
    Parser,
    Reporter,
    load_skill_aliases,
    load_stopwords,
)
from models import AnalysisResult, Vacancy

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger("hirescope")


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def collect_vacancies(
    fetcher: Fetcher,
    parser: Parser,
    query: str,
    area: int,
    max_vacancies: int,
    experience: str | None,
) -> list[Vacancy]:
    vacancies: list[Vacancy] = []
    page = 0

    while len(vacancies) < max_vacancies:
        params: dict = {
            "text": query,
            "area": area,
            "per_page": SEARCH_PER_PAGE,
            "page": page,
        }
        if experience:
            params["experience"] = experience

        log.info(
            "Загрузка страницы поиска %d (собрано %d/%d)",
            page + 1,
            len(vacancies),
            max_vacancies,
        )

        html = fetcher.get(SEARCH_URL, params=params)
        items = parser.parse_search_page(html)

        if not items:
            log.info("Страница %d пуста — останавливаемся", page + 1)
            break

        for item in items:
            if len(vacancies) >= max_vacancies:
                break
            vacancies.append(Vacancy(
                id=item["id"],
                title=item["title"],
                url=item["url"],
            ))

        if not parser.has_next_page(html):
            log.info("Следующей страницы нет — останавливаемся")
            break

        page += 1

    return vacancies


def enrich_vacancies(
    fetcher: Fetcher,
    parser: Parser,
    vacancies: list[Vacancy],
) -> list[Vacancy]:
    total = len(vacancies)
    for i, vacancy in enumerate(vacancies, 1):
        log.info("[%d/%d] %s", i, total, vacancy.title)
        try:
            html = fetcher.get(vacancy.url)
            desc, skills = parser.parse_vacancy_page(html)
            vacancy.description_text = desc
            vacancy.skills = skills
        except Exception as e:
            log.warning("Ошибка при загрузке %s: %s", vacancy.url, e)
    return vacancies


def run(args: argparse.Namespace) -> None:
    stopwords = load_stopwords(extra_file=args.stopwords_file)
    skill_aliases = load_skill_aliases()

    fetcher = Fetcher(delay=args.delay, cache_dir=args.cache_dir)
    parser = Parser()
    analyzer = Analyzer(
        stopwords=stopwords,
        skill_aliases=skill_aliases,
        min_word_length=args.min_word_length,
        use_bigrams=args.bigrams,
    )

    vacancies = collect_vacancies(
        fetcher=fetcher,
        parser=parser,
        query=args.query,
        area=args.area,
        max_vacancies=args.max_vacancies,
        experience=args.experience,
    )

    if not vacancies:
        log.error("Вакансии не найдены. Проверьте запрос.")
        sys.exit(1)

    log.info("Найдено вакансий: %d", len(vacancies))
    vacancies = enrich_vacancies(fetcher, parser, vacancies)

    keyword_counter = analyzer.count_keywords(vacancies)
    skill_counter = analyzer.count_skills(vacancies)

    all_keywords = keyword_counter.most_common()
    all_skills = skill_counter.most_common()

    hot_keywords = [(w, c) for w, c in all_keywords if c >= args.keyword_threshold]
    hot_skills = [(s, c) for s, c in all_skills if c >= args.skill_threshold]

    result = AnalysisResult(
        query=args.query,
        total_vacancies=len(vacancies),
        hot_keywords=hot_keywords,
        hot_skills=hot_skills,
        all_keywords=all_keywords,
        all_skills=all_skills,
    )

    Reporter.print_console(result, top_n=args.top_n)

    if args.output_format in ("json", "both") and args.output_file:
        Reporter.save_json(result, args.output_file)

    if args.output_format in ("csv", "both") and args.output_file:
        Reporter.save_csv(result, args.output_file)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="hirescope",
        description="HireScope — анализатор горячих навыков и ключевых слов в вакансиях hh.ru",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    search = p.add_argument_group("Поиск")
    search.add_argument("--query", required=True, help='Поисковый запрос, например "Frontend Angular"')
    search.add_argument("--area", type=int, default=0, help="ID региона (0=все, 1=Москва, 2=СПб)")
    search.add_argument("--max-vacancies", type=int, default=DEFAULT_MAX_VACANCIES)
    search.add_argument("--experience", choices=EXPERIENCE_CHOICES, default=None)

    analysis = p.add_argument_group("Анализ")
    analysis.add_argument("--keyword-threshold", type=int, default=DEFAULT_KEYWORD_THRESHOLD)
    analysis.add_argument("--skill-threshold", type=int, default=DEFAULT_SKILL_THRESHOLD)
    analysis.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    analysis.add_argument("--min-word-length", type=int, default=DEFAULT_MIN_WORD_LENGTH)
    analysis.add_argument("--stopwords-file", default=None, help="Дополнительный файл стоп-слов")
    analysis.add_argument("--bigrams", action="store_true", help="Включить биграммы в keyword-анализ")

    output = p.add_argument_group("Вывод")
    output.add_argument("--output-format", choices=["console", "json", "csv", "both"], default="console")
    output.add_argument("--output-file", default="hirescope_results.json")

    technical = p.add_argument_group("Технические")
    technical.add_argument("--delay", type=float, default=DEFAULT_REQUEST_DELAY)
    technical.add_argument("--cache-dir", default=None)
    technical.add_argument("--verbose", action="store_true")

    return p


if __name__ == "__main__":
    args = build_cli().parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    run(args)