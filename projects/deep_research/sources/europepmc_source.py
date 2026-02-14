"""Europe PMC API integration for biomedical and life sciences research."""

from typing import List, Optional
import httpx
from ..models import ResearchResult

EUROPEPMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def search_papers(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search Europe PMC for biomedical and life sciences publications.

    Europe PMC provides access to 40M+ life sciences publications including
    PubMed, PubMed Central, and preprint servers.

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="europepmc"

    Raises:
        Exception: If the Europe PMC API request fails
    """
    try:
        # Build query with date filtering
        query = topic

        # Add date filtering using FIRST_PDATE field
        # Europe PMC uses year-based filtering with 3000 representing "present"
        if date_from or date_to:
            from_year = date_from[:4] if date_from else "1900"
            to_year = date_to[:4] if date_to else "3000"
            query += f" FIRST_PDATE:[{from_year} TO {to_year}]"

        # Build search parameters
        params: dict[str, str | int] = {
            "query": query,
            "format": "json",
            "pageSize": min(max_results, 1000),  # Max page size
            "resultType": "core",  # Get full result including abstracts
        }

        # Make API request
        response = httpx.get(EUROPEPMC_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        results: List[ResearchResult] = []

        # Extract results from nested structure
        result_list = data.get("resultList", {}).get("result", [])

        for item in result_list:
            # Skip if no title
            if not item.get("title"):
                continue

            # Extract publication date
            pub_year = item.get("pubYear", "")
            pub_date = f"{pub_year}-01-01" if pub_year else ""

            # Extract authors - use authorString for simplicity
            authors = []
            author_string = item.get("authorString", "")
            if author_string:
                # Split by comma and clean up
                authors = [a.strip() for a in author_string.split(",")[:10]]

            # Get abstract
            abstract = item.get("abstractText", "")
            if not abstract:
                # Build metadata description if no abstract
                abstract_parts = []

                journal_info = item.get("journalInfo", {})
                journal = journal_info.get("journal", {})
                journal_title = journal.get("title", "")
                if journal_title:
                    abstract_parts.append(f"Journal: {journal_title}")

                pub_type_list = item.get("pubTypeList", {}).get("pubType", [])
                if pub_type_list:
                    pub_types = ", ".join(pub_type_list[:3])
                    abstract_parts.append(f"Type: {pub_types}")

                is_open_access = item.get("isOpenAccess", "N")
                access_label = "Open Access" if is_open_access == "Y" else "Closed Access"
                abstract_parts.append(f"Access: {access_label}")

                abstract = " | ".join(abstract_parts) if abstract_parts else "No abstract available"

            # Get URL - prefer DOI, fallback to fullTextUrl
            url = item.get("doi", "")
            if url and not url.startswith("http"):
                url = f"https://doi.org/{url}"
            if not url:
                # Try to get URL from fullTextUrlList
                full_text_urls = item.get("fullTextUrlList", {}).get("fullTextUrl", [])
                if full_text_urls:
                    url = full_text_urls[0].get("url", "")
            if not url:
                # Fallback to Europe PMC URL using PMID or ID
                pmid = item.get("pmid", "")
                if pmid:
                    url = f"https://europepmc.org/article/MED/{pmid}"
                else:
                    item_id = item.get("id", "")
                    source = item.get("source", "MED")
                    if item_id:
                        url = f"https://europepmc.org/article/{source}/{item_id}"

            results.append(
                ResearchResult(
                    title=item["title"],
                    abstract=abstract.replace("\n", " ").strip(),
                    url=url,
                    published_date=pub_date,
                    source="europepmc",
                    authors=authors,
                )
            )

        return results

    except httpx.HTTPStatusError as e:
        raise Exception(f"Europe PMC API error (HTTP {e.response.status_code}): {e}")
    except Exception as e:
        raise Exception(f"Failed to search Europe PMC: {e}")
