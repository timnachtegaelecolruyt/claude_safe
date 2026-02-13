"""Tests for the source selector module."""

import pytest
from unittest.mock import patch
from projects.deep_research.synthesis.source_selector import select_sources, _format_source_descriptions


@pytest.fixture
def all_sources():
    """All available sources."""
    return ["arxiv", "web", "news", "semantic_scholar", "hackernews"]


@pytest.fixture
def source_descriptions():
    """Source descriptions for testing."""
    return {"arxiv": "Academic research papers", "web": "General web content", "news": "Recent news articles"}


def test_select_sources_empty_list():
    """Test with empty source list."""
    selected, reasoning = select_sources("test topic", [], verbose=False)
    assert selected == []
    assert reasoning == {}


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_industry_topic(mock_ollama, all_sources):
    """Test source selection for industry/engineering topic."""
    # Mock LLM to exclude arXiv for industry topic
    mock_ollama.return_value = """{
  "selected": ["news", "web", "semantic_scholar"],
  "reasoning": {
    "news": "Industry topic likely to have announcements",
    "web": "Practical tooling information",
    "semantic_scholar": "May have relevant research",
    "arxiv": "Too academic for this industry topic",
    "hackernews": "Not directly relevant"
  }
}"""

    selected, reasoning = select_sources("data platform metadata management", all_sources, verbose=False)

    assert len(selected) == 3
    assert "arxiv" not in selected
    assert "news" in selected
    assert "web" in selected
    assert "semantic_scholar" in selected
    assert "news" in reasoning
    assert "arxiv" in reasoning


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_academic_topic(mock_ollama, all_sources):
    """Test source selection for academic/research topic."""
    # Mock LLM to include arXiv and Semantic Scholar for academic topic
    mock_ollama.return_value = """{
  "selected": ["arxiv", "semantic_scholar"],
  "reasoning": {
    "arxiv": "Academic topic with research papers",
    "semantic_scholar": "Citations and scholarly work",
    "news": "Unlikely to have relevant news",
    "web": "Not enough academic content",
    "hackernews": "Community discussions not needed"
  }
}"""

    selected, reasoning = select_sources("quantum error correction algorithms", all_sources, verbose=False)

    assert len(selected) == 2
    assert "arxiv" in selected
    assert "semantic_scholar" in selected
    assert "hackernews" not in selected


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_tech_community_topic(mock_ollama, all_sources):
    """Test source selection for tech/community topic."""
    # Mock LLM to include HackerNews for community topics
    mock_ollama.return_value = """{
  "selected": ["web", "hackernews", "news"],
  "reasoning": {
    "web": "Practical guides and tutorials",
    "hackernews": "Community opinions and trends",
    "news": "Recent developments",
    "arxiv": "Not research-focused",
    "semantic_scholar": "Not academic"
  }
}"""

    selected, reasoning = select_sources("React hooks best practices", all_sources, verbose=False)

    assert len(selected) == 3
    assert "hackernews" in selected
    assert "web" in selected
    assert "news" in selected


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_too_few_selected(mock_ollama, all_sources):
    """Test fallback when LLM selects fewer than 2 sources."""
    # Mock LLM to select only 1 source
    mock_ollama.return_value = """{
  "selected": ["arxiv"],
  "reasoning": {
    "arxiv": "Only relevant source"
  }
}"""

    selected, reasoning = select_sources("test topic", all_sources, verbose=False)

    # Should fallback to all sources
    assert len(selected) == len(all_sources)
    assert "fallback" in reasoning


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_json_parse_error(mock_ollama, all_sources):
    """Test fallback when JSON parsing fails."""
    # Mock LLM to return invalid JSON
    mock_ollama.return_value = "This is not valid JSON {incomplete"

    selected, reasoning = select_sources("test topic", all_sources, verbose=False)

    # Should fallback to all sources
    assert selected == all_sources
    assert "error" in reasoning


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_json_in_codeblock(mock_ollama, all_sources):
    """Test parsing JSON from markdown code block."""
    # Mock LLM to return JSON in code block
    mock_ollama.return_value = """```json
{
  "selected": ["news", "web"],
  "reasoning": {
    "news": "Relevant",
    "web": "Relevant"
  }
}
```"""

    selected, reasoning = select_sources("test topic", all_sources, verbose=False)

    assert len(selected) == 2
    assert "news" in selected
    assert "web" in selected


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_exception_handling(mock_ollama, all_sources):
    """Test fallback when exception occurs."""
    # Mock LLM to raise exception
    mock_ollama.side_effect = Exception("API Error")

    selected, reasoning = select_sources("test topic", all_sources, verbose=False)

    # Should fallback to all sources
    assert selected == all_sources
    assert "error" in reasoning


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_invalid_source_names(mock_ollama):
    """Test filtering out invalid source names."""
    available = ["arxiv", "web", "news"]

    # Mock LLM to return some invalid source names
    mock_ollama.return_value = """{
  "selected": ["arxiv", "invalid_source", "web"],
  "reasoning": {
    "arxiv": "Relevant",
    "invalid_source": "This doesn't exist",
    "web": "Relevant"
  }
}"""

    selected, reasoning = select_sources("test topic", available, verbose=False)

    # Should filter out invalid sources
    assert len(selected) == 2
    assert "arxiv" in selected
    assert "web" in selected
    assert "invalid_source" not in selected


def test_format_source_descriptions(source_descriptions):
    """Test source description formatting."""
    formatted = _format_source_descriptions(source_descriptions)

    assert "**arxiv**" in formatted
    assert "**web**" in formatted
    assert "**news**" in formatted
    assert "Academic research papers" in formatted
    assert "General web content" in formatted
    assert "Recent news articles" in formatted


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_verbose_output(mock_ollama, all_sources, capsys):
    """Test verbose output during source selection."""
    mock_ollama.return_value = """{
  "selected": ["news", "web"],
  "reasoning": {
    "news": "Industry announcements",
    "web": "Practical guides"
  }
}"""

    selected, reasoning = select_sources("test topic", all_sources, verbose=True)

    captured = capsys.readouterr()
    assert "Analyzing topic" in captured.out
    assert "Selected 2/5 sources" in captured.out
    assert "news: Industry announcements" in captured.out


@patch("projects.deep_research.synthesis.source_selector._call_ollama")
def test_select_sources_ensures_minimum_two(mock_ollama):
    """Test that at least 2 sources are selected when available."""
    available = ["arxiv", "web"]

    # Mock LLM to select only 1 source
    mock_ollama.return_value = """{
  "selected": ["arxiv"],
  "reasoning": {
    "arxiv": "Only relevant"
  }
}"""

    selected, reasoning = select_sources("test topic", available, verbose=False)

    # Should fallback to both sources
    assert len(selected) == 2
