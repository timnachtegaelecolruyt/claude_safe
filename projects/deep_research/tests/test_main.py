"""Tests for CLI entry point and source orchestration."""

from unittest.mock import patch, MagicMock
from projects.deep_research.models import ResearchQuery, ResearchResult
from projects.deep_research.main import _collect_results, ALL_SOURCES


def _make_query(topic: str = "test") -> ResearchQuery:
    return ResearchQuery(topic=topic, max_results=2)


def _make_result(source: str) -> ResearchResult:
    return ResearchResult(
        title=f"Result from {source}",
        abstract="Abstract text.",
        url="https://example.com",
        published_date="2024-01-01",
        source=source,
        authors=["Author"],
    )


class TestCollectResults:
    @patch("projects.deep_research.main.arxiv_search")
    def test_single_source(self, mock_arxiv: MagicMock) -> None:
        mock_arxiv.return_value = [_make_result("arxiv")]

        results = _collect_results(_make_query(), ["arxiv"])

        assert len(results) == 1
        assert results[0].source == "arxiv"
        mock_arxiv.assert_called_once()

    @patch("projects.deep_research.main.search_stories")
    @patch("projects.deep_research.main.scholar_search")
    @patch("projects.deep_research.main.search_news")
    @patch("projects.deep_research.main.search_web")
    @patch("projects.deep_research.main.arxiv_search")
    def test_all_sources(
        self,
        mock_arxiv: MagicMock,
        mock_web: MagicMock,
        mock_news: MagicMock,
        mock_scholar: MagicMock,
        mock_hn: MagicMock,
    ) -> None:
        mock_arxiv.return_value = [_make_result("arxiv")]
        mock_web.return_value = [_make_result("web")]
        mock_news.return_value = [_make_result("news")]
        mock_scholar.return_value = [_make_result("semantic_scholar")]
        mock_hn.return_value = [_make_result("hackernews")]

        results = _collect_results(_make_query(), ALL_SOURCES)

        assert len(results) == 5
        sources = {r.source for r in results}
        assert sources == {"arxiv", "web", "news", "semantic_scholar", "hackernews"}

    @patch("projects.deep_research.main.search_web")
    @patch("projects.deep_research.main.arxiv_search")
    def test_source_failure_continues(self, mock_arxiv: MagicMock, mock_web: MagicMock) -> None:
        mock_arxiv.side_effect = Exception("arXiv is down")
        mock_web.return_value = [_make_result("web")]

        results = _collect_results(_make_query(), ["arxiv", "web"])

        # Should still get web results despite arXiv failure
        assert len(results) == 1
        assert results[0].source == "web"

    def test_unknown_source_skipped(self) -> None:
        results = _collect_results(_make_query(), ["nonexistent"])

        assert results == []

    @patch("projects.deep_research.main.arxiv_search")
    def test_empty_source_list(self, mock_arxiv: MagicMock) -> None:
        results = _collect_results(_make_query(), [])

        assert results == []
        mock_arxiv.assert_not_called()


class TestMainCLI:
    @patch("projects.deep_research.main.save_report")
    @patch("projects.deep_research.main.generate_markdown")
    @patch("projects.deep_research.main.analyze_research")
    @patch("projects.deep_research.main._collect_results")
    def test_full_pipeline(
        self,
        mock_collect: MagicMock,
        mock_analyze: MagicMock,
        mock_generate: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        mock_collect.return_value = [_make_result("arxiv")]
        mock_analyze.return_value = {"summary": "Test summary", "insights": ["Insight 1"]}
        mock_generate.return_value = "# Report"
        mock_save.return_value = "/tmp/report.md"

        from projects.deep_research.main import main

        with patch("sys.argv", ["main", "--topic", "test topic", "--max-results", "5"]):
            main()

        mock_collect.assert_called_once()
        mock_analyze.assert_called_once()
        mock_generate.assert_called_once()
        mock_save.assert_called_once()

    @patch("projects.deep_research.main._collect_results")
    def test_no_results_exits(self, mock_collect: MagicMock) -> None:
        mock_collect.return_value = []

        from projects.deep_research.main import main
        import pytest

        with patch("sys.argv", ["main", "--topic", "nothing"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    @patch("projects.deep_research.main.save_report")
    @patch("projects.deep_research.main.generate_markdown")
    @patch("projects.deep_research.main.analyze_research")
    @patch("projects.deep_research.main._collect_results")
    def test_exclude_source_flag(
        self,
        mock_collect: MagicMock,
        mock_analyze: MagicMock,
        mock_generate: MagicMock,
        mock_save: MagicMock,
    ) -> None:
        mock_collect.return_value = [_make_result("arxiv")]
        mock_analyze.return_value = {"summary": "S", "insights": ["I"]}
        mock_generate.return_value = "# R"
        mock_save.return_value = "/tmp/r.md"

        from projects.deep_research.main import main

        with patch("sys.argv", ["main", "--topic", "test", "--exclude-source", "hackernews,news"]):
            main()

        # Check that _collect_results was called without excluded sources
        call_args = mock_collect.call_args
        active_sources = call_args[0][1]
        assert "hackernews" not in active_sources
        assert "news" not in active_sources
        assert "arxiv" in active_sources
