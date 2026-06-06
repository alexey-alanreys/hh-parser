import csv
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from core.reporter import Reporter
from models import AnalysisResult


def make_result(**kwargs) -> AnalysisResult:
    defaults = dict(
        query="Frontend React",
        total_vacancies=20,
        hot_keywords=[("typescript", 8), ("angular", 6)],
        hot_skills=[("React", 14), ("TypeScript", 6)],
        all_keywords=[("typescript", 8), ("angular", 6), ("html", 3)],
        all_skills=[("React", 14), ("TypeScript", 6), ("CSS3", 2)],
    )
    defaults.update(kwargs)
    return AnalysisResult(**defaults)


class TestPrintConsole:
    def test_output_contains_query_and_count(self, capsys):
        Reporter.print_console(make_result(), top_n=10)
        out = capsys.readouterr().out
        assert "Frontend React" in out
        assert "20" in out

    def test_output_contains_skills_and_keywords(self, capsys):
        Reporter.print_console(make_result(), top_n=10)
        out = capsys.readouterr().out
        assert "React" in out
        assert "typescript" in out

    def test_empty_hot_lists(self, capsys):
        result = make_result(hot_keywords=[], hot_skills=[])
        Reporter.print_console(result, top_n=10)
        out = capsys.readouterr().out
        assert "нет результатов выше порога" in out

    def test_top_n_limits_output(self, capsys):
        keywords = [(f"word{i}", 10 - i) for i in range(10)]
        result = make_result(hot_keywords=keywords, all_keywords=keywords)
        Reporter.print_console(result, top_n=3)
        out = capsys.readouterr().out
        assert "word0" in out
        assert "word1" in out
        assert "word2" in out
        assert "word3" not in out


class TestSaveJson:
    def test_creates_valid_json(self, tmp_path):
        path = str(tmp_path / "out.json")
        Reporter.save_json(make_result(), path)
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert data["query"] == "Frontend React"
        assert data["total_vacancies"] == 20
        assert data["hot_skills"][0] == {"skill": "React", "count": 14}

    def test_all_fields_present(self, tmp_path):
        path = str(tmp_path / "out.json")
        Reporter.save_json(make_result(), path)
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        assert set(data.keys()) == {
            "query", "total_vacancies",
            "hot_skills", "hot_keywords",
            "all_skills", "all_keywords",
        }

    def test_cyrillic_not_escaped(self, tmp_path):
        path = str(tmp_path / "out.json")
        Reporter.save_json(make_result(), path)
        raw = Path(path).read_text(encoding="utf-8")
        assert "typescript" in raw
        assert "\\u" not in raw  # ensure_ascii=False работает


class TestSaveCsv:
    def test_creates_two_files(self, tmp_path):
        Reporter.save_csv(make_result(), str(tmp_path / "out.csv"))
        assert (tmp_path / "out_skills.csv").exists()
        assert (tmp_path / "out_keywords.csv").exists()

    def test_skills_csv_content(self, tmp_path):
        Reporter.save_csv(make_result(), str(tmp_path / "out.csv"))
        rows = list(csv.DictReader(open(tmp_path / "out_skills.csv", encoding="utf-8")))
        assert rows[0]["skill"] == "React"
        assert rows[0]["count"] == "14"
        assert rows[0]["hot"] == "True"
        assert rows[2]["hot"] == "False"  # CSS3 не в hot

    def test_keywords_csv_has_header(self, tmp_path):
        Reporter.save_csv(make_result(), str(tmp_path / "out.csv"))
        content = (tmp_path / "out_keywords.csv").read_text(encoding="utf-8")
        assert content.startswith("word,count,hot")