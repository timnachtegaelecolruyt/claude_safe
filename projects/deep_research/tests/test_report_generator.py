"""Tests for Markdown report generation."""

import os
import tempfile
from datetime import datetime
from unittest.mock import patch

from projects.deep_research.models import ResearchQuery, ResearchReport, ResearchResult
from projects.deep_research.report_generator import generate_markdown, save_report, SOURCE_LABELS


def _make_result(source: str = "arxiv", title: str = "Test Paper", **kwargs) -> ResearchResult:
    defaults = {
        "title": title,
        "abstract": "This is an abstract.",
        "url": "https://example.com/paper",
        "published_date": "2024-01-15",
        "source": source,
        "authors": ["Alice", "Bob"],
    }
    defaults.update(kwargs)
    return ResearchResult(**defaults)


def _make_report(**kwargs) -> ResearchReport:
    defaults = {
        "query": ResearchQuery(topic="test topic", max_results=10),
        "summary": "Executive summary text.",
        "insights": ["Insight one", "Insight two"],
        "results": [_make_result("arxiv"), _make_result("web", title="Web Article")],
        "generated_at": datetime(2024, 6, 15, 10, 30, 0),
    }
    defaults.update(kwargs)
    return ResearchReport(**defaults)


class TestGenerateMarkdown:
    def test_contains_topic(self) -> None:
        md = generate_markdown(_make_report())
        assert "test topic" in md

    def test_contains_summary(self) -> None:
        md = generate_markdown(_make_report())
        assert "Executive summary text." in md

    def test_contains_insights(self) -> None:
        md = generate_markdown(_make_report())
        assert "1. Insight one" in md
        assert "2. Insight two" in md

    def test_groups_by_source(self) -> None:
        md = generate_markdown(_make_report())
        assert SOURCE_LABELS["arxiv"] in md
        assert SOURCE_LABELS["web"] in md

    def test_results_contain_metadata(self) -> None:
        md = generate_markdown(_make_report())
        assert "**Authors**: Alice, Bob" in md
        assert "**Published**: 2024-01-15" in md
        assert "**Source**: arxiv" in md

    def test_no_results_section_when_empty(self) -> None:
        report = _make_report(results=[])
        md = generate_markdown(report)
        assert "found)" not in md

    def test_no_insights_section_when_empty(self) -> None:
        report = _make_report(insights=[])
        md = generate_markdown(report)
        assert "Key Insights" not in md

    def test_skips_empty_published_date(self) -> None:
        result = _make_result(published_date="")
        report = _make_report(results=[result])
        md = generate_markdown(report)
        assert "**Published**:" not in md

    def test_skips_empty_url(self) -> None:
        result = _make_result(url="")
        report = _make_report(results=[result])
        md = generate_markdown(report)
        assert "**URL**:" not in md

    def test_many_authors_truncated(self) -> None:
        result = _make_result(authors=["A", "B", "C", "D", "E", "F", "G"])
        report = _make_report(results=[result])
        md = generate_markdown(report)
        assert "et al." in md

    def test_unknown_source_uses_title_case(self) -> None:
        result = _make_result(source="custom_src")
        report = _make_report(results=[result])
        md = generate_markdown(report)
        assert "Custom_Src" in md

    def test_footer_contains_model(self) -> None:
        md = generate_markdown(_make_report())
        assert "Ollama" in md


class TestSaveReport:
    def test_saves_with_custom_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("projects.deep_research.report_generator.config") as mock_cfg:
                mock_cfg.output_dir = tmpdir
                mock_cfg.ollama_model = "test-model"

                path = save_report("# Test", filename="custom.md")

                assert path == os.path.join(tmpdir, "custom.md")
                with open(path) as f:
                    assert f.read() == "# Test"

    def test_saves_with_generated_filename(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("projects.deep_research.report_generator.config") as mock_cfg:
                mock_cfg.output_dir = tmpdir
                mock_cfg.ollama_model = "test-model"

                path = save_report("# Auto")

                assert path.endswith(".md")
                assert "research_report_" in path
                assert os.path.exists(path)

    def test_creates_output_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = os.path.join(tmpdir, "sub", "dir")
            with patch("projects.deep_research.report_generator.config") as mock_cfg:
                mock_cfg.output_dir = nested
                mock_cfg.ollama_model = "test-model"

                path = save_report("# Nested", filename="test.md")

                assert os.path.exists(path)
