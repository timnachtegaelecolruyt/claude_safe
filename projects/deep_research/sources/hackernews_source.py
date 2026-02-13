"""HackerNews search integration via Algolia API."""

from typing import List
from datetime import datetime
import httpx
from ..models import ResearchResult

HN_SEARCH_API = "https://hn.algolia.com/api/v1/search"


def search_stories(topic: str, max_results: int = 10) -> List[ResearchResult]:
    """
    Search HackerNews for stories and discussions related to the topic.

    Args:
        topic: Search query string
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="hackernews"

    Raises:
        Exception: If the HN Algolia API request fails
    """
    try:
        params = {
            "query": topic,
            "tags": "story",
            "hitsPerPage": min(max_results, 50),
        }

        response = httpx.get(HN_SEARCH_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        results: List[ResearchResult] = []
        for hit in data.get("hits", []):
            title = hit.get("title", "")
            if not title:
                continue

            # Use the linked URL if available, otherwise the HN discussion link
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"

            # Parse created_at timestamp
            created_at = hit.get("created_at", "")
            published_date = ""
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    published_date = dt.strftime("%Y-%m-%d")
                except (ValueError, AttributeError):
                    pass

            # Build a summary from available fields
            points = hit.get("points", 0)
            num_comments = hit.get("num_comments", 0)
            author = hit.get("author", "Unknown")
            story_text = hit.get("story_text") or ""
            abstract = story_text[:500] if story_text else f"{points} points, {num_comments} comments on HN"

            results.append(
                ResearchResult(
                    title=title,
                    abstract=abstract,
                    url=url,
                    published_date=published_date,
                    source="hackernews",
                    authors=[author],
                )
            )

        return results

    except httpx.HTTPStatusError as e:
        raise Exception(f"HackerNews API error (HTTP {e.response.status_code}): {e}")
    except Exception as e:
        raise Exception(f"Failed to search HackerNews: {e}")
