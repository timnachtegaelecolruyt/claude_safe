"""Tests for Semantic Scholar source integration."""

from unittest.mock import patch, MagicMock
from urllib.parse import urlparse
import httpx
from projects.deep_research.sources.scholar_source import search_papers
from projects.deep_research.models import ResearchResult


def _mock_scholar_response():
    return {
        "data": [
            {
                "title": "Attention Is All You Need",
                "abstract": (
                    "The dominant sequence transduction models are based on complex recurrent or "
                    "convolutional neural networks."
                ),
                "url": "https://www.semanticscholar.org/paper/123",
                "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}],
                "year": 2017,
                "externalIds": {"DOI": "10.48550/arXiv.1706.03762", "ArXiv": "1706.03762"},
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "abstract": "We introduce a new language representation model called BERT.",
                "url": "",
                "authors": [{"name": "Jacob Devlin"}],
                "year": 2019,
                "externalIds": {"DOI": "10.18653/v1/N19-1423"},
            },
            {
                "title": "No Abstract Paper",
                "abstract": None,
                "url": "",
                "authors": [],
                "year": None,
                "externalIds": None,
            },
        ]
    }


class TestSearchPapers:
    @patch("projects.deep_research.sources.scholar_source.httpx.get")
    def test_returns_research_results(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = _mock_scholar_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_papers(topic="transformer architecture", max_results=5)

        assert len(results) == 3
        assert all(isinstance(r, ResearchResult) for r in results)
        assert all(r.source == "semantic_scholar" for r in results)
        assert results[0].title == "Attention Is All You Need"
        assert results[0].published_date == "2017-01-01"
        assert "Ashish Vaswani" in results[0].authors

    @patch("projects.deep_research.sources.scholar_source.httpx.get")
    def test_url_fallback_to_doi(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _mock_scholar_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_papers(topic="bert", max_results=5)

        # Second paper has empty url but has DOI
        parsed_url = urlparse(results[1].url)
        assert parsed_url.netloc == "doi.org"

    @patch("projects.deep_research.sources.scholar_source.httpx.get")
    def test_handles_missing_abstract(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = _mock_scholar_response()
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_papers(topic="test", max_results=5)

        assert results[2].abstract == "No abstract available"

    @patch("projects.deep_research.sources.scholar_source.httpx.get")
    def test_date_filter_passes_year_param(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        search_papers(topic="llm", date_from="2023-01-01", date_to="2024-12-31", max_results=5)

        call_kwargs = mock_get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params")
        assert params["year"] == "2023-2024"

    @patch("projects.deep_research.sources.scholar_source.httpx.get")
    def test_empty_results(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = search_papers(topic="nonexistent", max_results=5)

        assert results == []

    @patch("projects.deep_research.sources.scholar_source.httpx.get")
    def test_http_error_raises(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Rate limited", request=MagicMock(), response=mock_response
        )
        mock_get.return_value = mock_response

        try:
            search_papers(topic="test", max_results=5)
            assert False, "Should have raised"
        except Exception as e:
            assert "Semantic Scholar API error" in str(e)
