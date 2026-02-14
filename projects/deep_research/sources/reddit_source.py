"""Reddit search integration for community discussions and insights."""

from datetime import datetime
from typing import List, Optional
import httpx
from ..models import ResearchResult

REDDIT_SEARCH_API = "https://www.reddit.com/search.json"


def search_posts(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search Reddit for community discussions related to the topic.

    Uses Reddit's public JSON API (no authentication required).

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="reddit"

    Raises:
        Exception: If the Reddit API request fails
    """
    try:
        params: dict[str, str | int] = {
            "q": topic,
            "sort": "relevance",
            "limit": min(max_results, 100),
            "type": "link",
        }

        # Reddit uses time-based filters: hour, day, week, month, year, all
        # Map date_from to the closest time filter
        if date_from:
            params["t"] = _date_to_time_filter(date_from)
        else:
            params["t"] = "year"

        headers = {
            "User-Agent": "DeepResearchTool/1.0",
        }

        response = httpx.get(REDDIT_SEARCH_API, params=params, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        results: List[ResearchResult] = []
        children = data.get("data", {}).get("children", [])

        for child in children:
            post = child.get("data", {})

            if not post.get("title"):
                continue

            # Extract creation date
            created_utc = post.get("created_utc", 0)
            pub_date = ""
            if created_utc:
                pub_date = datetime.utcfromtimestamp(created_utc).strftime("%Y-%m-%d")

            # Filter by date range if specified
            if date_from and pub_date and pub_date < date_from:
                continue
            if date_to and pub_date and pub_date > date_to:
                continue

            # Build abstract from selftext or use title
            selftext = post.get("selftext", "")
            subreddit = post.get("subreddit", "")
            num_comments = post.get("num_comments", 0)
            score = post.get("score", 0)

            abstract_parts = []
            if subreddit:
                abstract_parts.append(f"r/{subreddit}")
            abstract_parts.append(f"Score: {score} | Comments: {num_comments}")
            if selftext:
                # Truncate long selftext
                abstract_parts.append(selftext[:500])

            abstract = " | ".join(abstract_parts) if abstract_parts else "No description available"

            # Build URL
            permalink = post.get("permalink", "")
            url = f"https://www.reddit.com{permalink}" if permalink else post.get("url", "")

            # Author
            author = post.get("author", "")
            authors = [f"u/{author}"] if author and author != "[deleted]" else []

            results.append(
                ResearchResult(
                    title=post["title"],
                    abstract=abstract.replace("\n", " ").strip(),
                    url=url,
                    published_date=pub_date,
                    source="reddit",
                    authors=authors,
                )
            )

        return results

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise Exception("Reddit API rate limit exceeded. Please wait and retry.")
        raise Exception(f"Reddit API error (HTTP {e.response.status_code}): {e}")
    except Exception as e:
        raise Exception(f"Failed to search Reddit: {e}")


def _date_to_time_filter(date_from: str) -> str:
    """Convert a date string to Reddit's time filter parameter."""
    try:
        from_date = datetime.strptime(date_from, "%Y-%m-%d")
        days_ago = (datetime.now() - from_date).days

        if days_ago <= 1:
            return "day"
        elif days_ago <= 7:
            return "week"
        elif days_ago <= 30:
            return "month"
        elif days_ago <= 365:
            return "year"
        else:
            return "all"
    except ValueError:
        return "year"
