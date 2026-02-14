"""GitHub search API integration for open source project discovery."""

import os
from typing import List, Optional
import httpx
from ..models import ResearchResult

GITHUB_SEARCH_API = "https://api.github.com/search/repositories"


def search_repos(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search GitHub for repositories related to the topic.

    Uses GitHub's public search API. Optionally set GITHUB_TOKEN env var
    for higher rate limits (30 req/min vs 10 req/min).

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="github"

    Raises:
        Exception: If the GitHub API request fails
    """
    try:
        # Build query with date filtering
        query = topic

        if date_from and date_to:
            query += f" pushed:{date_from}..{date_to}"
        elif date_from:
            query += f" pushed:>={date_from}"
        elif date_to:
            query += f" pushed:<={date_to}"

        params: dict[str, str | int] = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": min(max_results, 100),
        }

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DeepResearchTool/1.0",
        }

        # Use token if available for higher rate limits
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"

        response = httpx.get(GITHUB_SEARCH_API, params=params, headers=headers, timeout=30.0)
        response.raise_for_status()
        data = response.json()

        results: List[ResearchResult] = []

        for repo in data.get("items", []):
            if not repo.get("name"):
                continue

            # Extract dates
            updated_at = repo.get("updated_at", "")
            pub_date = updated_at[:10] if updated_at else ""

            # Build description with metadata
            description = repo.get("description", "") or ""
            stars = repo.get("stargazers_count", 0)
            forks = repo.get("forks_count", 0)
            language = repo.get("language", "")
            topics = repo.get("topics", [])

            abstract_parts = []
            if description:
                abstract_parts.append(description[:300])

            meta_parts = []
            if stars:
                meta_parts.append(f"Stars: {stars:,}")
            if forks:
                meta_parts.append(f"Forks: {forks:,}")
            if language:
                meta_parts.append(f"Language: {language}")
            if meta_parts:
                abstract_parts.append(" | ".join(meta_parts))

            if topics:
                abstract_parts.append(f"Topics: {', '.join(topics[:5])}")

            abstract = " | ".join(abstract_parts) if abstract_parts else "No description available"

            # Author is the repo owner
            owner = repo.get("owner", {})
            owner_login = owner.get("login", "")
            authors = [owner_login] if owner_login else []

            results.append(
                ResearchResult(
                    title=repo.get("full_name", repo["name"]),
                    abstract=abstract.replace("\n", " ").strip(),
                    url=repo.get("html_url", ""),
                    published_date=pub_date,
                    source="github",
                    authors=authors,
                )
            )

        return results

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 403:
            raise Exception("GitHub API rate limit exceeded. Set GITHUB_TOKEN env var for higher limits.")
        raise Exception(f"GitHub API error (HTTP {e.response.status_code}): {e}")
    except Exception as e:
        raise Exception(f"Failed to search GitHub: {e}")
