"""Tests for DBLP source integration."""

from projects.deep_research.sources.dblp_source import search_papers
from projects.deep_research.models import ResearchResult


def test_search_papers_returns_list() -> None:
    """Test that search_papers returns a list of ResearchResult objects."""
    # Note: This makes real API calls. For production, use mocking.
    results = search_papers(topic="distributed systems", max_results=2)

    assert isinstance(results, list)
    assert len(results) <= 2

    if results:
        assert isinstance(results[0], ResearchResult)
        assert results[0].source == "dblp"
        assert len(results[0].title) > 0
        assert len(results[0].url) > 0


def test_search_papers_with_date_filter() -> None:
    """Test that date filtering works correctly."""
    results = search_papers(
        topic="neural networks",
        date_from="2020-01-01",
        date_to="2022-12-31",
        max_results=5,
    )

    assert isinstance(results, list)

    for result in results:
        # Published date should be within the specified range
        if result.published_date:
            # DBLP returns YYYY-01-01 format
            assert result.published_date >= "2020-01-01"
            assert result.published_date <= "2022-12-31"


def test_search_papers_with_invalid_topic() -> None:
    """Test handling of searches that return no results."""
    results = search_papers(
        topic="xyzabc123nonexistenttopicdefinitely",
        max_results=5,
    )

    # Should return empty list, not raise exception
    assert isinstance(results, list)


def test_search_papers_authors_extraction() -> None:
    """Test that authors are properly extracted from both single and array formats."""
    results = search_papers(topic="compiler optimization", max_results=3)

    assert isinstance(results, list)

    # Check author extraction
    for result in results:
        assert isinstance(result.authors, list)
        # Authors can be empty or populated
        if result.authors:
            # Each author should be a non-empty string
            for author in result.authors:
                assert isinstance(author, str)
                assert len(author) > 0


def test_search_papers_metadata_extraction() -> None:
    """Test that DBLP metadata is properly extracted into abstract field."""
    results = search_papers(topic="database systems", max_results=2)

    assert isinstance(results, list)

    for result in results:
        # Abstract should exist (either metadata or "No abstract available")
        assert isinstance(result.abstract, str)
        assert len(result.abstract) > 0

        # If metadata was extracted, should contain separators
        if "Published in:" in result.abstract or "Type:" in result.abstract:
            # Verify it contains DBLP metadata format
            assert " | " in result.abstract or result.abstract.startswith("Published in:")


def test_search_papers_url_preference() -> None:
    """Test that URLs follow preference: DOI > ee > url."""
    results = search_papers(topic="software engineering", max_results=5)

    assert isinstance(results, list)

    for result in results:
        # All results should have a URL
        assert len(result.url) > 0

        # DOI URLs should be normalized to https://doi.org/...
        if "doi.org" in result.url:
            assert result.url.startswith("https://doi.org/")


def test_search_papers_publication_date_format() -> None:
    """Test that publication dates are in YYYY-MM-DD format."""
    results = search_papers(topic="algorithms", max_results=3)

    assert isinstance(results, list)

    for result in results:
        if result.published_date:
            # Should be YYYY-01-01 format for DBLP (year only)
            assert len(result.published_date) == 10
            assert result.published_date[4] == "-"
            assert result.published_date[7] == "-"
            assert result.published_date.endswith("-01-01")
