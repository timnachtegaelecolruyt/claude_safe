"""Tests for the relevance filter module."""

import pytest
from unittest.mock import patch
from projects.deep_research.models import ResearchQuery, ResearchResult
from projects.deep_research.synthesis.filter import filter_relevant_results, _judge_relevance


@pytest.fixture
def sample_query():
    """Create a sample research query."""
    return ResearchQuery(topic="machine learning for healthcare", max_results=10)


@pytest.fixture
def sample_results():
    """Create sample research results with varying relevance."""
    return [
        ResearchResult(
            title="Deep Learning for Medical Image Analysis",
            abstract="This paper presents a novel deep learning approach for analyzing medical images...",
            url="https://example.com/1",
            published_date="2024-01-15",
            source="arxiv",
            authors=["John Doe"],
        ),
        ResearchResult(
            title="Quantum Computing Applications in Astronomy",
            abstract="We explore quantum algorithms for astronomical data processing...",
            url="https://example.com/2",
            published_date="2024-02-10",
            source="arxiv",
            authors=["Jane Smith"],
        ),
        ResearchResult(
            title="AI-Powered Healthcare Diagnostics",
            abstract="Machine learning models for early disease detection in clinical settings...",
            url="https://example.com/3",
            published_date="2024-03-05",
            source="web",
            authors=[],
        ),
    ]


def test_filter_relevant_results_empty():
    """Test filtering with no results."""
    query = ResearchQuery(topic="test topic", max_results=10)
    filtered, stats = filter_relevant_results(query, [], verbose=False)

    assert filtered == []
    assert stats["total"] == 0
    assert stats["relevant"] == 0
    assert stats["filtered_out"] == 0


@patch("projects.deep_research.synthesis.filter._call_ollama_judge")
def test_filter_relevant_results_all_relevant(mock_ollama, sample_query, sample_results):
    """Test filtering when all results are relevant."""
    # Mock Ollama to return all relevant
    mock_ollama.return_value = '{"relevant": true, "reason": "Directly related to topic"}'

    filtered, stats = filter_relevant_results(sample_query, sample_results, verbose=False)

    assert len(filtered) == len(sample_results)
    assert stats["total"] == 3
    assert stats["relevant"] == 3
    assert stats["filtered_out"] == 0


@patch("projects.deep_research.synthesis.filter._call_ollama_judge")
def test_filter_relevant_results_mixed(mock_ollama, sample_query, sample_results):
    """Test filtering with mixed relevant/irrelevant results."""

    # Mock Ollama to return different judgments
    def mock_judgment(prompt):
        if "Quantum Computing" in prompt:
            return '{"relevant": false, "reason": "Not related to healthcare"}'
        return '{"relevant": true, "reason": "Related to healthcare ML"}'

    mock_ollama.side_effect = mock_judgment

    filtered, stats = filter_relevant_results(sample_query, sample_results, verbose=False)

    assert len(filtered) == 2  # Should filter out quantum computing paper
    assert stats["total"] == 3
    assert stats["relevant"] == 2
    assert stats["filtered_out"] == 1
    assert all("Quantum" not in r.title for r in filtered)


@patch("projects.deep_research.synthesis.filter._call_ollama_judge")
def test_judge_relevance_json_response(mock_ollama):
    """Test _judge_relevance with valid JSON response."""
    mock_ollama.return_value = '{"relevant": true, "reason": "Directly related"}'

    result = ResearchResult(
        title="Test Paper",
        abstract="Test abstract",
        url="https://example.com",
        published_date="2024-01-01",
        source="arxiv",
        authors=[],
    )

    is_relevant, reason = _judge_relevance("machine learning", result)
    assert is_relevant is True
    assert reason == "Directly related"


@patch("projects.deep_research.synthesis.filter._call_ollama_judge")
def test_judge_relevance_json_in_codeblock(mock_ollama):
    """Test _judge_relevance with JSON in markdown code block."""
    mock_ollama.return_value = '```json\n{"relevant": false, "reason": "Unrelated"}\n```'

    result = ResearchResult(
        title="Test Paper",
        abstract="Test abstract",
        url="https://example.com",
        published_date="2024-01-01",
        source="arxiv",
        authors=[],
    )

    is_relevant, reason = _judge_relevance("machine learning", result)
    assert is_relevant is False
    assert reason == "Unrelated"


@patch("projects.deep_research.synthesis.filter._call_ollama_judge")
def test_judge_relevance_fallback_parsing(mock_ollama):
    """Test _judge_relevance with non-JSON response (fallback)."""
    mock_ollama.return_value = "Yes, this is relevant because..."

    result = ResearchResult(
        title="Test Paper",
        abstract="Test abstract",
        url="https://example.com",
        published_date="2024-01-01",
        source="arxiv",
        authors=[],
    )

    is_relevant, reason = _judge_relevance("machine learning", result)
    # Fallback should look for keywords
    assert is_relevant is False  # "true" keyword not found
    assert "fallback" in reason.lower()


@patch("projects.deep_research.synthesis.filter._call_ollama_judge")
def test_judge_relevance_error_handling(mock_ollama):
    """Test _judge_relevance handles errors gracefully."""
    mock_ollama.side_effect = Exception("API Error")

    result = ResearchResult(
        title="Test Paper",
        abstract="Test abstract",
        url="https://example.com",
        published_date="2024-01-01",
        source="arxiv",
        authors=[],
    )

    # Should default to True (keep result) on error
    is_relevant, reason = _judge_relevance("machine learning", result)
    assert is_relevant is True
    assert "Error" in reason
