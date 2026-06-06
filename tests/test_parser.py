import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parser import Parser

SEARCH_HTML = """
<html><body>
  <a data-qa="serp-item__title" href="https://hh.ru/vacancy/111?query=test">
    <span data-qa="serp-item__title-text">Frontend Developer</span>
  </a>
  <a data-qa="serp-item__title" href="https://hh.ru/vacancy/222?query=test">
    <span data-qa="serp-item__title-text">Angular Разработчик</span>
  </a>
  <a data-qa="pager-next" href="/search/vacancy?page=1">Следующая</a>
</body></html>
"""

SEARCH_HTML_LAST = """
<html><body>
  <a data-qa="serp-item__title" href="https://hh.ru/vacancy/333">
    <span data-qa="serp-item__title-text">React Developer</span>
  </a>
</body></html>
"""

VACANCY_HTML = """
<html><body>
  <div data-qa="vacancy-description">
    Требуется опытный разработчик. Знание TypeScript обязательно.
    Опыт работы с Angular и React.
  </div>
  <ul>
    <li data-qa="skills-element"><div><div>TypeScript</div></div></li>
    <li data-qa="skills-element"><div><div>Angular</div></div></li>
    <li data-qa="skills-element"><div><div>React</div></div></li>
  </ul>
</body></html>
"""

VACANCY_HTML_NO_SKILLS = """
<html><body>
  <div data-qa="vacancy-description">Описание без навыков.</div>
</body></html>
"""


class TestParseSearchPage:
    def test_extracts_vacancies(self):
        items = Parser.parse_search_page(SEARCH_HTML)
        assert len(items) == 2
        assert items[0]["id"] == "111"
        assert items[0]["title"] == "Frontend Developer"
        assert items[0]["url"] == "https://hh.ru/vacancy/111"

    def test_empty_html(self):
        assert Parser.parse_search_page("<html><body></body></html>") == []

    def test_deduplicates_ids(self):
        html = """
        <html><body>
          <a data-qa="serp-item__title" href="https://hh.ru/vacancy/123">
            <span data-qa="serp-item__title-text">Job A</span>
          </a>
          <a data-qa="serp-item__title" href="https://hh.ru/vacancy/123">
            <span data-qa="serp-item__title-text">Job A copy</span>
          </a>
        </body></html>
        """
        items = Parser.parse_search_page(html)
        assert len(items) == 1
        assert items[0]["id"] == "123"

    def test_ignores_links_without_vacancy_id(self):
        html = """
        <html><body>
          <a data-qa="serp-item__title" href="https://hh.ru/employer/456">
            <span data-qa="serp-item__title-text">Not a vacancy</span>
          </a>
        </body></html>
        """
        assert Parser.parse_search_page(html) == []


class TestParseVacancyPage:
    def test_extracts_description_and_skills(self):
        desc, skills = Parser.parse_vacancy_page(VACANCY_HTML)
        assert "TypeScript" in desc
        assert "Angular" in desc
        assert set(skills) == {"TypeScript", "Angular", "React"}

    def test_no_skills_returns_empty_list(self):
        desc, skills = Parser.parse_vacancy_page(VACANCY_HTML_NO_SKILLS)
        assert "Описание без навыков" in desc
        assert skills == []

    def test_no_description_returns_empty_string(self):
        html = "<html><body><li data-qa='skills-element'>Git</li></body></html>"
        desc, skills = Parser.parse_vacancy_page(html)
        assert desc == ""
        assert skills == ["Git"]


class TestHasNextPage:
    def test_true_when_pager_present(self):
        assert Parser.has_next_page(SEARCH_HTML) is True

    def test_false_when_no_pager(self):
        assert Parser.has_next_page(SEARCH_HTML_LAST) is False