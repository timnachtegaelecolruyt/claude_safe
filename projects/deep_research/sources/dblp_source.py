"""DBLP API integration for computer science bibliography."""

from typing import List, Optional
import httpx
from ..models import ResearchResult

DBLP_API = "https://dblp.org/search/publ/api"


def search_papers(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search DBLP for computer science publications matching the topic.

    DBLP is a comprehensive computer science bibliography covering
    journals, conferences, workshops, and more since the 1960s.

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="dblp"

    Raises:
        Exception: If the DBLP API request fails
    """
    try:
        # Build search parameters
        params: dict[str, str | int] = {
            "q": topic,
            "format": "json",
            "h": min(max_results, 1000),  # DBLP caps at 1000
        }

        # Make API request
        response = httpx.get(DBLP_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        results: List[ResearchResult] = []

        # Extract hits from nested structure
        hits = data.get("result", {}).get("hits", {}).get("hit", [])

        for hit in hits:
            info = hit.get("info", {})

            # Skip if no title
            if not info.get("title"):
                continue

            # Extract publication year
            year = info.get("year", "")
            pub_date = f"{year}-01-01" if year else ""

            # Filter by date range if specified
            if date_from and pub_date and pub_date < date_from:
                continue
            if date_to and pub_date and pub_date > date_to:
                continue

            # Extract authors - can be single object or array
            authors = []
            authors_data = info.get("authors", {}).get("author", [])

            # Handle both single author (dict) and multiple authors (list)
            if isinstance(authors_data, dict):
                authors_data = [authors_data]
            elif not isinstance(authors_data, list):
                authors_data = []

            for author in authors_data[:10]:  # Limit to first 10
                if isinstance(author, dict):
                    author_name = author.get("text", "")
                    if author_name:
                        authors.append(author_name)

            # Get URL - prefer DOI, fallback to electronic edition, then DBLP URL
            url = info.get("doi", "")
            if url and not url.startswith("http"):
                url = f"https://doi.org/{url}"
            if not url:
                url = info.get("ee", "")
            if not url:
                url = info.get("url", "")

            # Build abstract from available metadata
            # DBLP doesn't provide abstracts, so create informative description
            abstract_parts = []

            venue = info.get("venue", "")
            if venue:
                abstract_parts.append(f"Published in: {venue}")

            pub_type = info.get("type", "")
            if pub_type:
                abstract_parts.append(f"Type: {pub_type}")

            pages = info.get("pages", "")
            if pages:
                abstract_parts.append(f"Pages: {pages}")

            access = info.get("access", "")
            if access:
                access_label = "Open Access" if access == "open" else "Closed Access"
                abstract_parts.append(f"Access: {access_label}")

            abstract = " | ".join(abstract_parts) if abstract_parts else "No abstract available"

            results.append(
                ResearchResult(
                    title=info["title"],
                    abstract=abstract,
                    url=url,
                    published_date=pub_date,
                    source="dblp",
                    authors=authors,
                )
            )

        return results

    except httpx.HTTPStatusError as e:
        raise Exception(f"DBLP API error (HTTP {e.response.status_code}): {e}")
    except Exception as e:
        raise Exception(f"Failed to search DBLP: {e}")
