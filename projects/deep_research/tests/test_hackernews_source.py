"""Tests for HackerNews source integration."""

from unittest.mock import patch, MagicMock
import httpx
from projects.deep_research.sources.hackernews_source import search_stories
from projects.deep_research.models import ResearchResult


def _mock_hn_response():
    return {
        "hits": [
            {
                "title": "Show HN: We built a Kubernetes operator for databases",
                "url": "https://example.com/k8s-operator",
                "objectID": "12345",
                "created_at": "2024-03-15T10:30:00Z",
                "points": 250,
                "num_comments": 85,
                "author": "devuser",
                "story_text": None,
            },
            {
                "title": "Ask HN: How do you handle Kubernetes in production?",
                "url": None,
                "objectID": "67890",
                "created_at": "2024-02-10T08:00:00Z",
                "points": 120,
                "num_comments": 200,
                "author": "sysadmin42",
                "story_text": "We've been running K8s for 2 years and have some questions about best practices.",
            },
        ]
    }


class TestSearchStories:
    @patch("projects.deep_research.sources.hackernews_source.httpx.get")
    def test_returns_research_results(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _mock_hn_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_stories(topic="kubernetes", max_results=5)

        assert len(results) == 2
        assert all(isinstance(r, ResearchResult) for r in results)
        assert all(r.source == "hackernews" for r in results)

    @patch("projects.deep_research.sources.hackernews_source.httpx.get")
    def test_uses_external_url_when_available(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _mock_hn_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_stories(topic="kubernetes", max_results=5)

        assert results[0].url == "https://example.com/k8s-operator"

    @patch("projects.deep_research.sources.hackernews_source.httpx.get")
    def test_falls_back_to_hn_url(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _mock_hn_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_stories(topic="kubernetes", max_results=5)

        # Second story has no external URL, should use HN discussion link
        assert "news.ycombinator.com" in results[1].url
        assert "67890" in results[1].url

    @patch("projects.deep_research.sources.hackernews_source.httpx.get")
    def test_parses_metadata(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _mock_hn_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_stories(topic="kubernetes", max_results=5)

        assert results[0].published_date == "2024-03-15"
        assert results[0].authors == ["devuser"]

    @patch("projects.deep_research.sources.hackernews_source.httpx.get")
    def test_story_text_used_as_abstract(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _mock_hn_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_stories(topic="kubernetes", max_results=5)

        # First story has no story_text, should use points/comments summary
        assert "250 points" in results[0].abstract
        # Second story has story_text
        assert "best practices" in results[1].abstract

    @patch("projects.deep_research.sources.hackernews_source.httpx.get")
    def test_empty_results(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"hits": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_stories(topic="nonexistent", max_results=5)

        assert results == []

    @patch("projects.deep_research.sources.hackernews_source.httpx.get")
    def test_http_error_raises(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=MagicMock(), response=mock_response
        )
        mock_get.return_value = mock_response

        try:
            search_stories(topic="test", max_results=5)
            assert False, "Should have raised"
        except Exception as e:
            assert "HackerNews API error" in str(e)
