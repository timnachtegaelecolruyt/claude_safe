"""Tests for DuckDuckGo web and news source integration."""

from unittest.mock import patch, MagicMock
from projects.deep_research.sources.web_source import search_web, search_news
from projects.deep_research.models import ResearchResult


def _mock_ddgs_text_results():
    return [
        {
            "title": "Kubernetes Adoption in Enterprise",
            "body": "Companies are rapidly adopting Kubernetes for container orchestration.",
            "href": "https://example.com/k8s-adoption",
        },
        {
            "title": "State of K8s 2024",
            "body": "Survey results from 500 enterprises on Kubernetes usage.",
            "href": "https://example.com/k8s-survey",
        },
    ]


def _mock_ddgs_news_results():
    return [
        {
            "title": "AI Startup Raises $100M",
            "body": "An artificial intelligence startup has raised a new funding round.",
            "url": "https://example.com/ai-funding",
            "date": "2024-06-15",
            "source": "TechCrunch",
        },
    ]


class TestSearchWeb:
    @patch("projects.deep_research.sources.web_source.DDGS")
    def test_returns_research_results(self, mock_ddgs_cls: MagicMock) -> None:
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.return_value = _mock_ddgs_text_results()
        mock_ddgs_cls.return_value = mock_ddgs

        results = search_web(topic="kubernetes", max_results=3)

        assert len(results) == 2
        assert all(isinstance(r, ResearchResult) for r in results)
        assert all(r.source == "web" for r in results)
        assert results[0].title == "Kubernetes Adoption in Enterprise"
        assert results[0].url == "https://example.com/k8s-adoption"

    @patch("projects.deep_research.sources.web_source.DDGS")
    def test_empty_results(self, mock_ddgs_cls: MagicMock) -> None:
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.text.return_value = []
        mock_ddgs_cls.return_value = mock_ddgs

        results = search_web(topic="nonexistent", max_results=3)

        assert results == []


class TestSearchNews:
    @patch("projects.deep_research.sources.web_source.DDGS")
    def test_returns_research_results(self, mock_ddgs_cls: MagicMock) -> None:
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.news.return_value = _mock_ddgs_news_results()
        mock_ddgs_cls.return_value = mock_ddgs

        results = search_news(topic="artificial intelligence", max_results=3)

        assert len(results) == 1
        assert results[0].source == "news"
        assert results[0].title == "AI Startup Raises $100M"
        assert results[0].published_date == "2024-06-15"
        assert results[0].authors == ["TechCrunch"]

    @patch("projects.deep_research.sources.web_source.DDGS")
    def test_empty_results(self, mock_ddgs_cls: MagicMock) -> None:
        mock_ddgs = MagicMock()
        mock_ddgs.__enter__ = MagicMock(return_value=mock_ddgs)
        mock_ddgs.__exit__ = MagicMock(return_value=False)
        mock_ddgs.news.return_value = []
        mock_ddgs_cls.return_value = mock_ddgs

        results = search_news(topic="nonexistent", max_results=3)

        assert results == []
