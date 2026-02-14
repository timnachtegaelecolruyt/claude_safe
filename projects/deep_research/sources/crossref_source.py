"""CrossRef API integration for scholarly research metadata."""

import os
import re
from typing import List, Optional
import httpx
from ..models import ResearchResult

CROSSREF_API = "https://api.crossref.org/works"


def search_papers(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search CrossRef for scholarly publications across all disciplines.

    CrossRef provides metadata for 140M+ scholarly works including journal
    articles, conference papers, books, and dissertations from publishers
    and repositories worldwide.

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="crossref"

    Raises:
        Exception: If the CrossRef API request fails

    Note:
        Uses polite pool for better reliability. Contact info from
        CROSSREF_MAILTO environment variable or defaults to project contact.
    """
    try:
        # Build filter for date range
        filters = []
        if date_from:
            filters.append(f"from-pub-date:{date_from}")
        if date_to:
            filters.append(f"until-pub-date:{date_to}")

        # Prefer records with abstracts
        filters.append("has-abstract:true")

        # Build search parameters
        params: dict[str, str | int] = {
            "query.bibliographic": topic,
            "rows": min(max_results, 1000),  # Max 1000 per request
            "sort": "relevance",
            "order": "desc",
            "select": "DOI,title,author,published,issued,abstract,URL,container-title,type,is-referenced-by-count",
        }

        if filters:
            params["filter"] = ",".join(filters)

        # Use polite pool with mailto parameter
        mailto = os.getenv("CROSSREF_MAILTO", "research@example.org")
        params["mailto"] = mailto

        # Set User-Agent header for polite pool
        headers = {"User-Agent": f"DeepResearchTool/1.0 (mailto:{mailto})"}

        # Make API request
        response = httpx.get(CROSSREF_API, params=params, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        results: List[ResearchResult] = []

        # Extract items from response
        items = data.get("message", {}).get("items", [])

        for item in items:
            # Skip if no title
            if not item.get("title"):
                continue

            # Extract title (it's an array)
            title = item["title"][0] if item["title"] else ""

            # Extract authors
            authors = []
            authors_data = item.get("author", [])
            for author in authors_data[:10]:  # Limit to first 10
                given = author.get("given", "")
                family = author.get("family", "")
                if family:
                    author_name = f"{given} {family}".strip()
                    authors.append(author_name)

            # Extract publication date from published or issued field
            pub_date = ""
            issued = item.get("published") or item.get("issued", {})
            if issued:
                date_parts = issued.get("date-parts", [[]])[0]
                if date_parts and date_parts[0] is not None:
                    year = date_parts[0]
                    month = date_parts[1] if len(date_parts) > 1 and date_parts[1] is not None else 1
                    day = date_parts[2] if len(date_parts) > 2 and date_parts[2] is not None else 1
                    pub_date = f"{year:04d}-{month:02d}-{day:02d}"

            # Extract and clean abstract (may contain JATS XML)
            abstract = item.get("abstract", "")
            if abstract:
                # Strip JATS XML tags if present
                if "<jats:" in abstract:
                    abstract = re.sub(r"<jats:[^>]+>", "", abstract)
                    abstract = re.sub(r"</jats:[^>]+>", "", abstract)
                abstract = abstract.replace("\n", " ").strip()
            else:
                # Build metadata description if no abstract
                abstract_parts = []

                container = item.get("container-title", [])
                if container:
                    abstract_parts.append(f"Published in: {container[0]}")

                work_type = item.get("type", "")
                if work_type:
                    # Clean up type name
                    type_display = work_type.replace("-", " ").title()
                    abstract_parts.append(f"Type: {type_display}")

                citations = item.get("is-referenced-by-count", 0)
                if citations:
                    abstract_parts.append(f"Citations: {citations}")

                abstract = " | ".join(abstract_parts) if abstract_parts else "No abstract available"

            # Get URL - prefer URL field, fallback to DOI
            url = item.get("URL", "")
            if not url:
                doi = item.get("DOI", "")
                if doi:
                    url = f"https://doi.org/{doi}"

            results.append(
                ResearchResult(
                    title=title,
                    abstract=abstract,
                    url=url,
                    published_date=pub_date,
                    source="crossref",
                    authors=authors,
                )
            )

        return results

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise Exception("CrossRef API rate limit exceeded. Please wait and retry.")
        raise Exception(f"CrossRef API error (HTTP {e.response.status_code}): {e}")
    except Exception as e:
        raise Exception(f"Failed to search CrossRef: {e}")
