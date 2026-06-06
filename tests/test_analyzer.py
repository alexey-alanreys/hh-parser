import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import Analyzer, load_skill_aliases, load_stopwords
from models import Vacancy


def make_vacancy(desc: str = "", skills: list[str] | None = None) -> Vacancy:
    return Vacancy(id="1", title="T", url="u", description_text=desc, skills=skills or [])


STOPWORDS = load_stopwords()
ALIASES = load_skill_aliases()


class TestLoadStopwords:
    def test_loads_from_file(self):
        words = load_stopwords()
        assert len(words) > 0
        assert "и" in words
        assert "знания" in words
        assert "участие" in words

    def test_new_stopwords_present(self):
        words = load_stopwords()
        assert "есть" in words
        assert "code" in words
        assert "части" in words
        assert "команду" in words
        assert "rest" in words
        assert "api" in words

    def test_ignores_comments(self):
        words = load_stopwords()
        assert not any(w.startswith("#") for w in words)

    def test_extra_file_not_found_doesnt_crash(self):
        words = load_stopwords(extra_file="/nonexistent/path.txt")
        assert len(words) > 0


class TestLoadSkillAliases:
    def test_loads_from_file(self):
        aliases = load_skill_aliases()
        assert len(aliases) > 0

    def test_keys_are_lowercase(self):
        aliases = load_skill_aliases()
        assert all(k == k.lower() for k in aliases)

    def test_known_alias(self):
        aliases = load_skill_aliases()
        assert aliases.get("react.js") == "React"
        assert aliases.get("java script") == "JavaScript"

    def test_ignore_aliases_present(self):
        aliases = load_skill_aliases()
        assert aliases.get("frontend") == "_ignore"
        assert aliases.get("front-end") == "_ignore"

    def test_comment_keys_excluded(self):
        aliases = load_skill_aliases()
        assert "_comment" not in aliases


class TestAnalyzerKeywords:
    def setup_method(self):
        self.analyzer = Analyzer(stopwords=STOPWORDS, skill_aliases=ALIASES)

    def test_counts_words(self):
        vacancies = [
            make_vacancy("разработка angular typescript разработка"),
            make_vacancy("разработка typescript frontend"),
        ]
        counter = self.analyzer.count_keywords(vacancies)
        assert counter["разработка"] == 3
        assert counter["typescript"] == 2

    def test_filters_stopwords(self):
        vacancies = [make_vacancy("знания участие typescript понимание")]
        counter = self.analyzer.count_keywords(vacancies)
        assert "знания" not in counter
        assert "участие" not in counter
        assert "typescript" in counter

    def test_filters_new_stopwords(self):
        vacancies = [make_vacancy("есть code части команду rest api typescript")]
        counter = self.analyzer.count_keywords(vacancies)
        assert "есть" not in counter
        assert "code" not in counter
        assert "rest" not in counter
        assert "api" not in counter
        assert "typescript" in counter

    def test_min_word_length(self):
        analyzer = Analyzer(stopwords=set(), skill_aliases={}, min_word_length=5)
        vacancies = [make_vacancy("api react angular")]
        counter = analyzer.count_keywords(vacancies)
        assert "api" not in counter
        assert "react" in counter
        assert "angular" in counter

    def test_bigrams_enabled(self):
        analyzer = Analyzer(stopwords=set(), skill_aliases={}, use_bigrams=True)
        vacancies = [make_vacancy("разработка frontend приложений")]
        counter = analyzer.count_keywords(vacancies)
        assert "разработка frontend" in counter
        assert "frontend приложений" in counter

    def test_bigrams_disabled_by_default(self):
        vacancies = [make_vacancy("разработка frontend приложений")]
        counter = self.analyzer.count_keywords(vacancies)
        assert "разработка frontend" not in counter

    def test_empty_description(self):
        counter = self.analyzer.count_keywords([make_vacancy("")])
        assert len(counter) == 0


class TestAnalyzerSkills:
    def setup_method(self):
        self.analyzer = Analyzer(stopwords=STOPWORDS, skill_aliases=ALIASES)

    def test_normalizes_via_aliases(self):
        vacancies = [make_vacancy(skills=["react.js", "React", "TypeScript", "java script"])]
        counter = self.analyzer.count_skills(vacancies)
        assert counter["React"] == 2
        assert counter["JavaScript"] == 1
        assert counter["TypeScript"] == 1

    def test_normalizes_case_without_alias(self):
        vacancies = [make_vacancy(skills=["figma", "FIGMA", "Figma"])]
        counter = self.analyzer.count_skills(vacancies)
        assert counter.get("Figma", 0) == 3

    def test_strips_whitespace(self):
        vacancies = [make_vacancy(skills=["  TypeScript  ", "Angular"])]
        counter = self.analyzer.count_skills(vacancies)
        assert counter["TypeScript"] == 1

    def test_empty_skills(self):
        counter = self.analyzer.count_skills([make_vacancy(skills=[])])
        assert len(counter) == 0

    def test_saas_normalized_to_sass(self):
        vacancies = [make_vacancy(skills=["saas", "sass", "scss"])]
        counter = self.analyzer.count_skills(vacancies)
        assert counter["SASS/SCSS"] == 3

    def test_ignored_skills_excluded(self):
        """frontend, front-end — не навыки, отфильтровываются через _ignore"""
        vacancies = [make_vacancy(skills=["frontend", "front-end", "React", "TypeScript"])]
        counter = self.analyzer.count_skills(vacancies)
        assert "Frontend" not in counter
        assert "_ignore" not in counter
        assert counter["React"] == 1
        assert counter["TypeScript"] == 1