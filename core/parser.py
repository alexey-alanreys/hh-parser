"""
HireScope — парсер HTML страниц hh.ru.
Использует только data-qa селекторы — они стабильны при редизайне вёрстки.
"""

import logging
import re

from bs4 import BeautifulSoup

from config import (
    SELECTOR_DESCRIPTION,
    SELECTOR_PAGER_NEXT,
    SELECTOR_SKILL,
    SELECTOR_VACANCY_TITLE_LINK,
    SELECTOR_VACANCY_TITLE_TEXT,
    VACANCY_URL,
)

log = logging.getLogger("hirescope.parser")


class Parser:
    @staticmethod
    def parse_search_page(html: str) -> list[dict[str, str]]:
        """
        Извлекает список вакансий со страницы поиска.
        Возвращает: [{"id": "...", "title": "...", "url": "..."}, ...]
        """
        soup = BeautifulSoup(html, "lxml")
        results: list[dict[str, str]] = []
        seen_ids: set[str] = set()

        for tag in soup.select(SELECTOR_VACANCY_TITLE_LINK):
            href = tag.get("href", "")
            match = re.search(r"/vacancy/(\d+)", href)
            if not match:
                continue

            vacancy_id = match.group(1)
            if vacancy_id in seen_ids:
                continue
            seen_ids.add(vacancy_id)

            title_tag = tag.select_one(SELECTOR_VACANCY_TITLE_TEXT)
            title = title_tag.get_text(strip=True) if title_tag else tag.get_text(strip=True)

            results.append({
                "id": vacancy_id,
                "title": title,
                "url": f"{VACANCY_URL}/{vacancy_id}",
            })

        return results

    @staticmethod
    def parse_vacancy_page(html: str) -> tuple[str, list[str]]:
        """
        Извлекает текст описания и список навыков со страницы вакансии.
        Возвращает: (description_text, skills)
        """
        soup = BeautifulSoup(html, "lxml")

        desc_block = soup.select_one(SELECTOR_DESCRIPTION)
        description_text = (
            desc_block.get_text(separator=" ", strip=True) if desc_block else ""
        )

        skills: list[str] = []
        for skill_el in soup.select(SELECTOR_SKILL):
            text = skill_el.get_text(strip=True)
            if text:
                skills.append(text)

        return description_text, skills

    @staticmethod
    def has_next_page(html: str) -> bool:
        soup = BeautifulSoup(html, "lxml")
        return bool(soup.select_one(SELECTOR_PAGER_NEXT))