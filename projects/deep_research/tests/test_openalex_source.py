"""Tests for OpenAlex source integration."""

from projects.deep_research.sources.openalex_source import search_papers, _extract_abstract
from projects.deep_research.models import ResearchResult


def test_search_papers_returns_list() -> None:
    """Test that search_papers returns a list of ResearchResult objects."""
    # Note: This makes real API calls. For production, use mocking.
    results = search_papers(topic="quantum computing", max_results=2)

    assert isinstance(results, list)
    assert len(results) <= 2

    if results:
        assert isinstance(results[0], ResearchResult)
        assert results[0].source == "openalex"
        assert len(results[0].title) > 0
        assert len(results[0].url) > 0


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
        # Published date should be within the specified range
        if result.published_date:
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


def test_extract_abstract_with_inverted_index() -> None:
    """Test abstract extraction from OpenAlex inverted index format."""
    inverted_index = {
        "This": [0],
        "is": [1],
        "a": [2],
        "test": [3],
        "abstract": [4],
    }

    abstract = _extract_abstract(inverted_index)

    assert abstract == "This is a test abstract"


def test_extract_abstract_with_none() -> None:
    """Test abstract extraction with None input."""
    abstract = _extract_abstract(None)

    assert abstract == ""


def test_extract_abstract_with_empty_dict() -> None:
    """Test abstract extraction with empty dictionary."""
    abstract = _extract_abstract({})

    assert abstract == ""


def test_extract_abstract_with_complex_index() -> None:
    """Test abstract extraction with repeated words at different positions."""
    inverted_index = {
        "The": [0, 5],
        "quick": [1],
        "brown": [2],
        "fox": [3],
        "jumps": [4],
        "over": [6],
        "lazy": [7],
        "dog": [8],
    }

    abstract = _extract_abstract(inverted_index)

    # Should reconstruct: "The quick brown fox jumps The over lazy dog"
    words = abstract.split()
    assert len(words) == 9
    assert words[0] == "The"
    assert words[5] == "The"
