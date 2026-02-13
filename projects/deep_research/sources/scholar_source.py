"""Semantic Scholar API integration for academic and industry paper research."""

from typing import List, Optional
import httpx
from ..models import ResearchResult

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,abstract,url,authors,year,externalIds"


def search_papers(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search Semantic Scholar for papers matching the topic.

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="semantic_scholar"

    Raises:
        Exception: If the Semantic Scholar API request fails
    """
    try:
        params: dict[str, str | int] = {
            "query": topic,
            "limit": min(max_results, 100),
            "fields": FIELDS,
        }

        # Semantic Scholar uses year range, extract years from dates
        if date_from:
            year_from = date_from[:4]
            year_to = date_to[:4] if date_to else "2099"
            params["year"] = f"{year_from}-{year_to}"

        response = httpx.get(SEMANTIC_SCHOLAR_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        results: List[ResearchResult] = []
        for paper in data.get("data", []):
            if not paper.get("title"):
                continue

            authors = [a["name"] for a in paper.get("authors", []) if a.get("name")]
            year = str(paper.get("year", ""))
            published_date = f"{year}-01-01" if year else ""

            # Build URL from externalIds or fallback
            paper_url = paper.get("url", "")
            external_ids = paper.get("externalIds", {}) or {}
            if not paper_url and external_ids.get("DOI"):
                paper_url = f"https://doi.org/{external_ids['DOI']}"
            if not paper_url and external_ids.get("ArXiv"):
                paper_url = f"https://arxiv.org/abs/{external_ids['ArXiv']}"

            results.append(
                ResearchResult(
                    title=paper["title"],
                    abstract=(paper.get("abstract") or "No abstract available").replace("\n", " ").strip(),
                    url=paper_url,
                    published_date=published_date,
                    source="semantic_scholar",
                    authors=authors,
                )
            )

        return results

    except httpx.HTTPStatusError as e:
        raise Exception(f"Semantic Scholar API error (HTTP {e.response.status_code}): {e}")
    except Exception as e:
        raise Exception(f"Failed to search Semantic Scholar: {e}")
