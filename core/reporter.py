"""
HireScope — форматирование и сохранение результатов анализа.
"""

import csv
import json
import logging
from pathlib import Path

from models import AnalysisResult

log = logging.getLogger("hirescope.reporter")

BAR_MAX_WIDTH = 40
BAR_CHAR = "█"


def _bar(count: int, max_count: int) -> str:
    if max_count == 0:
        return ""
    width = round(count / max_count * BAR_MAX_WIDTH)
    return BAR_CHAR * width


class Reporter:
    @staticmethod
    def print_console(result: AnalysisResult, top_n: int) -> None:
        print(f"\n{'=' * 60}")
        print("  HireScope — результаты анализа")
        print(f"{'=' * 60}")
        print(f"  Запрос:   {result.query}")
        print(f"  Вакансий: {result.total_vacancies}")
        print(f"{'=' * 60}\n")

        def _print_section(
            title: str,
            items: list[tuple[str, int]],
            top_n: int,
        ) -> None:
            sliced = items[:top_n]
            print(f"{title} (топ {len(sliced)}):")
            if not sliced:
                print("  — нет результатов выше порога\n")
                return
            max_count = sliced[0][1] if sliced else 1
            for label, count in sliced:
                print(f"  {label:<35} {count:>4}  {_bar(count, max_count)}")
            print()

        _print_section("🔥 ГОРЯЧИЕ НАВЫКИ", result.hot_skills, top_n)
        _print_section("🔑 ГОРЯЧИЕ КЛЮЧЕВЫЕ СЛОВА", result.hot_keywords, top_n)

    @staticmethod
    def save_json(result: AnalysisResult, path: str) -> None:
        data = {
            "query": result.query,
            "total_vacancies": result.total_vacancies,
            "hot_skills": [{"skill": s, "count": c} for s, c in result.hot_skills],
            "hot_keywords": [{"word": w, "count": c} for w, c in result.hot_keywords],
            "all_skills": [{"skill": s, "count": c} for s, c in result.all_skills],
            "all_keywords": [{"word": w, "count": c} for w, c in result.all_keywords],
        }
        Path(path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        log.info("JSON сохранён: %s", path)

    @staticmethod
    def save_csv(result: AnalysisResult, path: str) -> None:
        base = Path(path).stem
        parent = Path(path).parent
        hot_skills = {s for s, _ in result.hot_skills}
        hot_keywords = {w for w, _ in result.hot_keywords}

        skills_path = parent / f"{base}_skills.csv"
        with open(skills_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["skill", "count", "hot"])
            for skill, count in result.all_skills:
                writer.writerow([skill, count, skill in hot_skills])
        log.info("CSV навыков сохранён: %s", skills_path)

        keywords_path = parent / f"{base}_keywords.csv"
        with open(keywords_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["word", "count", "hot"])
            for word, count in result.all_keywords:
                writer.writerow([word, count, word in hot_keywords])
        log.info("CSV ключевых слов сохранён: %s", keywords_path)