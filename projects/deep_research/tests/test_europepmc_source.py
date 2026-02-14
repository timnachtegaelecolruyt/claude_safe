"""Tests for Europe PMC source integration."""

from projects.deep_research.sources.europepmc_source import search_papers
from projects.deep_research.models import ResearchResult


def test_search_papers_returns_list() -> None:
    """Test that search_papers returns a list of ResearchResult objects."""
    # Note: This makes real API calls. For production, use mocking.
    results = search_papers(topic="cancer immunotherapy", max_results=2)

    assert isinstance(results, list)
    assert len(results) <= 2

    if results:
        assert isinstance(results[0], ResearchResult)
        assert results[0].source == "europepmc"
        assert len(results[0].title) > 0
        assert len(results[0].url) > 0


def test_search_papers_with_date_filter() -> None:
    """Test that date filtering works correctly."""
    results = search_papers(
        topic="COVID-19",
        date_from="2020-01-01",
        date_to="2022-12-31",
        max_results=5,
    )

    assert isinstance(results, list)

    for result in results:
        # Published date should be within the specified range
        if result.published_date:
            # Europe PMC returns YYYY-01-01 format
            year = int(result.published_date[:4])
            assert year >= 2020
            assert year <= 2022


def test_search_papers_with_invalid_topic() -> None:
    """Test handling of searches that return no results."""
    results = search_papers(
        topic="xyzabc123nonexistenttopicdefinitely",
        max_results=5,
    )

    # Should return empty list, not raise exception
    assert isinstance(results, list)


def test_search_papers_authors_extraction() -> None:
    """Test that authors are properly extracted from authorString."""
    results = search_papers(topic="diabetes treatment", max_results=3)

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
    """Test that abstracts are properly extracted."""
    results = search_papers(topic="CRISPR gene editing", max_results=3)

    assert isinstance(results, list)

    for result in results:
        # Abstract should exist (either full text or metadata)
        assert isinstance(result.abstract, str)
        assert len(result.abstract) > 0

        # Should not contain newlines (replaced with spaces)
        assert "\n" not in result.abstract


def test_search_papers_url_generation() -> None:
    """Test that URLs are properly generated (DOI > fullText > Europe PMC)."""
    results = search_papers(topic="alzheimer disease", max_results=5)

    assert isinstance(results, list)

    for result in results:
        # All results should have a URL
        assert len(result.url) > 0

        # DOI URLs should be normalized to https://doi.org/...
        if "doi.org" in result.url:
            assert result.url.startswith("https://doi.org/")

        # Europe PMC URLs should be valid
        if "europepmc.org" in result.url:
            assert "europepmc.org/article/" in result.url


def test_search_papers_publication_date_format() -> None:
    """Test that publication dates are in YYYY-MM-DD format."""
    results = search_papers(topic="neuroscience", max_results=3)

    assert isinstance(results, list)

    for result in results:
        if result.published_date:
            # Should be YYYY-01-01 format for Europe PMC (year only)
            assert len(result.published_date) == 10
            assert result.published_date[4] == "-"
            assert result.published_date[7] == "-"
            assert result.published_date.endswith("-01-01")


def test_search_papers_biomedical_content() -> None:
    """Test that Europe PMC returns biomedical/life sciences content."""
    # Search for a distinctly biomedical topic
    results = search_papers(topic="cancer therapy", max_results=5)

    assert isinstance(results, list)

    # If results exist, check that they have scientific characteristics
    for result in results:
        # Should have title and abstract or metadata
        assert len(result.title) > 0
        assert len(result.abstract) > 0
