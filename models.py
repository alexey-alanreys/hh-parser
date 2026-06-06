"""
HireScope — модели данных.
"""

from dataclasses import dataclass, field


@dataclass
class Vacancy:
    id: str
    title: str
    url: str
    description_text: str = ""
    skills: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    query: str
    total_vacancies: int
    hot_keywords: list[tuple[str, int]]
    hot_skills: list[tuple[str, int]]
    all_keywords: list[tuple[str, int]]
    all_skills: list[tuple[str, int]]