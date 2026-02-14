"""Tests for CrossRef source integration."""

from urllib.parse import urlparse

from projects.deep_research.sources.crossref_source import search_papers
from projects.deep_research.models import ResearchResult


def test_search_papers_returns_list() -> None:
    """Test that search_papers returns a list of ResearchResult objects."""
    # Note: This makes real API calls. For production, use mocking.
    results = search_papers(topic="machine learning", max_results=2)

    assert isinstance(results, list)
    assert len(results) <= 2

    if results:
        assert isinstance(results[0], ResearchResult)
        assert results[0].source == "crossref"
        assert len(results[0].title) > 0
        assert len(results[0].url) > 0


def test_search_papers_with_date_filter() -> None:
    """Test that date filtering works correctly."""
    results = search_papers(
        topic="quantum computing",
        date_from="2023-01-01",
        date_to="2024-12-31",
        max_results=5,
    )

    assert isinstance(results, list)

    for result in results:
        # Published date should be within the specified range
        if result.published_date:
            year = int(result.published_date[:4])
            assert year >= 2023
            assert year <= 2024


def test_search_papers_with_invalid_topic() -> None:
    """Test handling of searches that return no results."""
    results = search_papers(
        topic="xyzabc123nonexistenttopicdefinitely",
        max_results=5,
    )

    # Should return empty list, not raise exception
    assert isinstance(results, list)


def test_search_papers_authors_extraction() -> None:
    """Test that authors are properly extracted from given/family names."""
    results = search_papers(topic="climate change", max_results=3)

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


def test_search_papers_abstract_extraction() -> None:
    """Test that abstracts are properly extracted and cleaned."""
    results = search_papers(topic="artificial intelligence", max_results=3)

    assert isinstance(results, list)

    for result in results:
        # Abstract should exist (either full text or metadata)
        assert isinstance(result.abstract, str)
        assert len(result.abstract) > 0

        # Should not contain newlines (replaced with spaces)
        assert "\n" not in result.abstract

        # Should not contain JATS XML tags (stripped in processing)
        assert "<jats:" not in result.abstract


def test_search_papers_url_generation() -> None:
    """Test that URLs are properly generated (URL field or DOI)."""
    results = search_papers(topic="renewable energy", max_results=5)

    assert isinstance(results, list)

    for result in results:
        # All results should have a URL
        assert len(result.url) > 0

        # URLs should be valid (either doi.org or other URLs)
        assert result.url.startswith("http://") or result.url.startswith("https://")

        # DOI URLs should be normalized
        parsed = urlparse(result.url)
        if parsed.netloc == "doi.org":
            assert result.url.startswith("https://doi.org/")


def test_search_papers_publication_date_format() -> None:
    """Test that publication dates are in YYYY-MM-DD format."""
    results = search_papers(topic="deep learning", max_results=3)

    assert isinstance(results, list)

    for result in results:
        if result.published_date:
            # Should be YYYY-MM-DD format
            assert len(result.published_date) == 10
            assert result.published_date[4] == "-"
            assert result.published_date[7] == "-"

            # Should be parseable as a date
            year = int(result.published_date[:4])
            month = int(result.published_date[5:7])
            day = int(result.published_date[8:10])

            assert 1900 <= year <= 2030
            assert 1 <= month <= 12
            assert 1 <= day <= 31


def test_search_papers_cross_disciplinary_content() -> None:
    """Test that CrossRef returns cross-disciplinary content."""
    # CrossRef covers all disciplines, test with diverse topics
    results = search_papers(topic="neural networks", max_results=5)

    assert isinstance(results, list)

    # If results exist, check that they have proper structure
    for result in results:
        # Should have title and abstract or metadata
        assert len(result.title) > 0
        assert len(result.abstract) > 0


def test_search_papers_metadata_fallback() -> None:
    """Test that metadata is used when abstracts are unavailable."""
    # Note: Some results may not have abstracts
    results = search_papers(topic="historical linguistics", max_results=10)

    assert isinstance(results, list)

    for result in results:
        # All should have some abstract text (real or metadata)
        assert len(result.abstract) > 0

        # Metadata fallback may contain "Published in:", "Type:", or "Citations:"
        # This is valid behavior when no abstract is available
