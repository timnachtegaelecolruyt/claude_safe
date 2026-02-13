"""Tests for LLM-powered research synthesis."""

from unittest.mock import patch, MagicMock
from projects.deep_research.models import ResearchQuery, ResearchResult
from projects.deep_research.synthesis.analyzer import (
    analyze_research,
    _build_research_context,
    _parse_response,
)


def _make_query(topic: str = "test topic") -> ResearchQuery:
    return ResearchQuery(topic=topic, max_results=5)


def _make_result(source: str = "arxiv", title: str = "Test Paper") -> ResearchResult:
    return ResearchResult(
        title=title,
        abstract="This is a test abstract for a research paper.",
        url="https://example.com/paper",
        published_date="2024-01-15",
        source=source,
        authors=["Alice", "Bob", "Charlie", "Diana"],
    )


class TestAnalyzeResearch:
    def test_empty_results_returns_no_data(self) -> None:
        result = analyze_research(_make_query(), [])

        assert "No research results found" in result["summary"]
        assert "No data available" in result["insights"][0]

    @patch("projects.deep_research.synthesis.analyzer._call_ollama")
    def test_calls_ollama_and_parses(self, mock_ollama: MagicMock) -> None:
        mock_ollama.return_value = """## Executive Summary
The research shows significant progress in test topic.

## Key Insights
1. First important insight about the field
2. Second important insight about trends
3. Third insight about future directions

## Notable Findings
- A particularly significant finding here"""

        results = [_make_result(), _make_result(source="web", title="Web Article")]
        analysis = analyze_research(_make_query(), results)

        assert "summary" in analysis
        assert "insights" in analysis
        assert len(analysis["insights"]) >= 2
        mock_ollama.assert_called_once()

    @patch("projects.deep_research.synthesis.analyzer._call_ollama")
    def test_prompt_includes_source_counts(self, mock_ollama: MagicMock) -> None:
        mock_ollama.return_value = "## Summary\nTest summary.\n## Insights\n1. Test insight number one here"

        results = [_make_result("arxiv"), _make_result("arxiv"), _make_result("web")]
        analyze_research(_make_query(), results)

        prompt = mock_ollama.call_args[0][0]
        assert "2 from arxiv" in prompt
        assert "1 from web" in prompt

    @patch("projects.deep_research.synthesis.analyzer._call_ollama")
    def test_ollama_failure_raises(self, mock_ollama: MagicMock) -> None:
        mock_ollama.side_effect = Exception("Connection refused")

        try:
            analyze_research(_make_query(), [_make_result()])
            assert False, "Should have raised"
        except Exception as e:
            assert "Failed to analyze research with LLM" in str(e)


class TestBuildResearchContext:
    def test_includes_all_results(self) -> None:
        results = [_make_result(title="Paper A"), _make_result(title="Paper B")]
        context = _build_research_context(results)

        assert "Paper A" in context
        assert "Paper B" in context
        assert "Paper 1:" in context
        assert "Paper 2:" in context

    def test_truncates_long_authors(self) -> None:
        result = _make_result()
        result.authors = ["A", "B", "C", "D", "E"]
        context = _build_research_context([result])

        assert "et al." in context

    def test_shows_unknown_for_no_authors(self) -> None:
        result = _make_result()
        result.authors = []
        context = _build_research_context([result])

        assert "Unknown" in context

    def test_includes_source_field(self) -> None:
        result = _make_result(source="hackernews")
        context = _build_research_context([result])

        assert "Source: hackernews" in context


class TestParseResponse:
    def test_structured_response(self) -> None:
        text = """## Executive Summary
The field is advancing rapidly with new breakthroughs.

## Key Insights
1. Neural networks are becoming more efficient
2. Transfer learning reduces training costs significantly
3. New architectures show promise for edge devices

## Notable Findings
- Edge computing adoption is accelerating in industry"""

        result = _parse_response(text)

        assert "advancing rapidly" in result["summary"]
        assert len(result["insights"]) >= 3

    def test_fallback_for_unstructured_response(self) -> None:
        text = """This is a general analysis of the research topic at hand.

The first trend we observe is that technology is evolving rapidly and companies are investing heavily.

The second major observation is that open source tools are becoming dominant in this space."""

        result = _parse_response(text)

        assert len(result["summary"]) > 0
        assert len(result["insights"]) >= 1

    def test_empty_response_uses_truncation(self) -> None:
        text = "Short."
        result = _parse_response(text)

        # Falls back to raw text as summary
        assert "Short." in result["summary"]
        assert result["insights"] == ["Analysis provided in summary"]

    def test_limits_to_10_insights(self) -> None:
        lines = ["## Key Insights"]
        for i in range(15):
            lines.append(f"{i+1}. This is insight number {i+1} which is long enough to pass the filter")
        text = "\n".join(lines)

        result = _parse_response(text)

        assert len(result["insights"]) <= 10

    def test_filters_short_insights(self) -> None:
        text = """## Key Insights
1. Too short
2. This insight is long enough to be meaningful and pass the minimum length check
3. Also short"""

        result = _parse_response(text)

        # Only the long one should pass the len > 10 filter
        assert len(result["insights"]) == 1
