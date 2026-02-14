"""CORE API integration for open access research papers."""

import os
from typing import List, Optional
import httpx
from ..models import ResearchResult

CORE_API = "https://api.core.ac.uk/v3/search/works/"


def search_papers(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search CORE for open access research papers.

    CORE aggregates 300M+ open access research papers from repositories
    and journals worldwide.

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="core"

    Raises:
        Exception: If the CORE API request fails

    Note:
        API key is optional. Set CORE_API_KEY environment variable for higher rate limits.
        Without API key: 100 requests/day, 10/minute
        With API key: 1000+ requests/day depending on tier
    """
    try:
        # Build query with date filtering
        query = topic

        # Add date filtering using yearPublished field
        if date_from or date_to:
            from_year = date_from[:4] if date_from else "1900"
            to_year = date_to[:4] if date_to else "2100"

            # Add year range filter using CORE query syntax
            if from_year == to_year:
                query += f" AND yearPublished:{from_year}"
            else:
                query += f" AND yearPublished>={from_year} AND yearPublished<={to_year}"

        # Build search parameters
        params: dict[str, str | int] = {
            "q": query,
            "limit": min(max_results, 100),  # CORE recommends max 100 per request
        }

        # Prepare headers with optional API key
        headers = {}
        api_key = os.getenv("CORE_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Make API request
        response = httpx.get(CORE_API, params=params, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        results: List[ResearchResult] = []

        # Extract results from response
        works = data.get("results", [])

        for work in works:
            # Skip if no title
            if not work.get("title"):
                continue

            # Extract authors
            authors = []
            authors_data = work.get("authors", [])
            for author in authors_data[:10]:  # Limit to first 10
                if isinstance(author, dict):
                    author_name = author.get("name", "")
                    if author_name:
                        authors.append(author_name)
                elif isinstance(author, str):
                    # Some entries may have authors as strings
                    authors.append(author)

            # Extract publication date
            pub_date = work.get("publishedDate", "")
            if not pub_date:
                # Fallback to yearPublished
                year = work.get("yearPublished")
                pub_date = f"{year}-01-01" if year else ""

            # Clean up date format (CORE returns ISO format, extract YYYY-MM-DD)
            if pub_date and "T" in pub_date:
                pub_date = pub_date.split("T")[0]

            # Get abstract
            abstract = work.get("abstract", "")
            if not abstract:
                # Build metadata description if no abstract
                abstract_parts = []

                doc_type = work.get("documentType", "")
                if doc_type:
                    abstract_parts.append(f"Type: {doc_type}")

                # Get data provider info
                data_providers = work.get("dataProviders", [])
                if data_providers:
                    provider_name = data_providers[0].get("name", "")
                    if provider_name:
                        abstract_parts.append(f"Repository: {provider_name}")

                citation_count = work.get("citationCount", 0)
                if citation_count:
                    abstract_parts.append(f"Citations: {citation_count}")

                abstract = " | ".join(abstract_parts) if abstract_parts else "No abstract available"

            # Get URL - prefer DOI, fallback to downloadUrl or CORE link
            url = work.get("doi", "")
            if url and not url.startswith("http"):
                url = f"https://doi.org/{url}"
            if not url:
                url = work.get("downloadUrl", "")
            if not url:
                # Fallback to CORE display URL
                work_id = work.get("id", "")
                if work_id:
                    url = f"https://core.ac.uk/works/{work_id}"

            results.append(
                ResearchResult(
                    title=work["title"],
                    abstract=abstract.replace("\n", " ").strip(),
                    url=url,
                    published_date=pub_date,
                    source="core",
                    authors=authors,
                )
            )

        return results

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise Exception(
                "CORE API rate limit exceeded. Consider setting CORE_API_KEY environment variable for higher limits."
            )
        raise Exception(f"CORE API error (HTTP {e.response.status_code}): {e}")
    except Exception as e:
        raise Exception(f"Failed to search CORE: {e}")
