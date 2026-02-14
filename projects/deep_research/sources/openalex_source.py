"""OpenAlex API integration for comprehensive scholarly research."""

from typing import List, Optional
import httpx
from ..models import ResearchResult

OPENALEX_API = "https://api.openalex.org/works"
# Polite pool: include email for faster response times
POLITE_POOL_EMAIL = "research@example.com"


def search_papers(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search OpenAlex for papers matching the topic.

    OpenAlex is a fully-open index of 474M+ scholarly works from various sources
    including journals, preprints, datasets, and books.

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="openalex"

    Raises:
        Exception: If the OpenAlex API request fails
    """
    try:
        # Build search parameters
        params: dict[str, str | int] = {
            "search": topic,
            "per-page": min(max_results, 100),  # Max 100 per page
            "sort": "publication_date:desc",
            "mailto": POLITE_POOL_EMAIL,  # Polite pool for faster responses
        }

        # Add date filtering using publication_date filter
        # OpenAlex format: from_publication_date:YYYY-MM-DD,to_publication_date:YYYY-MM-DD
        filter_parts = []
        if date_from:
            filter_parts.append(f"from_publication_date:{date_from}")
        if date_to:
            filter_parts.append(f"to_publication_date:{date_to}")

        if filter_parts:
            params["filter"] = ",".join(filter_parts)

        # Make API request
        response = httpx.get(OPENALEX_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        results: List[ResearchResult] = []
        for work in data.get("results", []):
            # Skip if no title
            if not work.get("title"):
                continue

            # Extract authors
            authorships = work.get("authorships", [])
            authors = []
            for authorship in authorships[:10]:  # Limit to first 10 authors
                author_info = authorship.get("author", {})
                if author_info and author_info.get("display_name"):
                    authors.append(author_info["display_name"])

            # Get publication date
            pub_date = work.get("publication_date", "")
            if not pub_date:
                # Fallback to publication year if date not available
                pub_year = work.get("publication_year")
                pub_date = f"{pub_year}-01-01" if pub_year else ""

            # Get abstract (inverted index format in OpenAlex)
            abstract = _extract_abstract(work.get("abstract_inverted_index"))
            if not abstract:
                abstract = "No abstract available"

            # Get URL - prefer DOI, fallback to OpenAlex URL
            url = work.get("doi", "")
            if not url:
                url = work.get("id", "")  # OpenAlex ID URL

            results.append(
                ResearchResult(
                    title=work["title"],
                    abstract=abstract.replace("\n", " ").strip(),
                    url=url,
                    published_date=pub_date,
                    source="openalex",
                    authors=authors,
                )
            )

        return results

    except httpx.HTTPStatusError as e:
        raise Exception(f"OpenAlex API error (HTTP {e.response.status_code}): {e}")
    except Exception as e:
        raise Exception(f"Failed to search OpenAlex: {e}")


def _extract_abstract(inverted_index: Optional[dict]) -> str:
    """
    Convert OpenAlex inverted index format to plain text abstract.

    OpenAlex stores abstracts in inverted index format for efficiency:
    {"word": [position1, position2], ...}

    Args:
        inverted_index: Dictionary mapping words to their positions

    Returns:
        Plain text abstract string
    """
    if not inverted_index:
        return ""

    try:
        # Build list of (position, word) tuples
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))

        # Sort by position and join words
        word_positions.sort(key=lambda x: x[0])
        abstract = " ".join([word for _, word in word_positions])

        return abstract

    except Exception:
        return ""
