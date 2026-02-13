"""DuckDuckGo web and news search integration."""

from typing import List
from duckduckgo_search import DDGS
from ..models import ResearchResult


def search_web(topic: str, max_results: int = 10) -> List[ResearchResult]:
    """
    Search the web for articles, reports, and pages related to the topic.

    Args:
        topic: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="web"

    Raises:
        Exception: If the DuckDuckGo search fails
    """
    try:
        results: List[ResearchResult] = []
        with DDGS() as ddgs:
            for hit in ddgs.text(topic, max_results=max_results):
                results.append(
                    ResearchResult(
                        title=hit.get("title", "Untitled"),
                        abstract=hit.get("body", ""),
                        url=hit.get("href", ""),
                        published_date="",
                        source="web",
                        authors=[],
                    )
                )
        return results

    except Exception as e:
        raise Exception(f"Failed to search web via DuckDuckGo: {e}")


def search_news(topic: str, max_results: int = 10) -> List[ResearchResult]:
    """
    Search DuckDuckGo news for recent articles related to the topic.

    Args:
        topic: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="news"

    Raises:
        Exception: If the DuckDuckGo news search fails
    """
    try:
        results: List[ResearchResult] = []
        with DDGS() as ddgs:
            for hit in ddgs.news(topic, max_results=max_results):
                results.append(
                    ResearchResult(
                        title=hit.get("title", "Untitled"),
                        abstract=hit.get("body", ""),
                        url=hit.get("url", ""),
                        published_date=hit.get("date", ""),
                        source="news",
                        authors=[hit.get("source", "Unknown")],
                    )
                )
        return results

    except Exception as e:
        raise Exception(f"Failed to search news via DuckDuckGo: {e}")
