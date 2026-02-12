"""Tests for arXiv source integration."""

from projects.deep_research.sources.arxiv_source import search_papers
from projects.deep_research.models import ResearchResult


def test_search_papers_returns_list() -> None:
    """Test that search_papers returns a list of ResearchResult objects."""
    # Note: This makes real API calls. For production, use mocking.
    results = search_papers(topic="quantum computing", max_results=2)

    assert isinstance(results, list)
    assert len(results) <= 2

    if results:
        assert isinstance(results[0], ResearchResult)
        assert results[0].source == "arxiv"
        assert len(results[0].title) > 0
        assert len(results[0].abstract) > 0


def test_search_papers_with_date_filter() -> None:
    """Test that date filtering works correctly."""
    results = search_papers(
        topic="machine learning",
        date_from="2024-01-01",
        date_to="2024-12-31",
        max_results=3,
    )

    assert isinstance(results, list)

    for result in results:
        assert result.published_date >= "2024-01-01"
        assert result.published_date <= "2024-12-31"


def test_search_papers_with_invalid_topic() -> None:
    """Test handling of searches that return no results."""
    results = search_papers(
        topic="xyzabc123nonexistenttopicdefinitely",
        max_results=5,
    )

    # Should return empty list, not raise exception
    assert isinstance(results, list)
