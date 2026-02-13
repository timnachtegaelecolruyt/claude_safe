"""arXiv API integration for academic paper research."""

from typing import List, Optional
import arxiv
from ..models import ResearchResult


def search_papers(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search arXiv for papers matching the topic.

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects

    Raises:
        Exception: If the arXiv API request fails
    """
    try:
        # Create arXiv search client
        client = arxiv.Client()

        # Build search query
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        # Execute search
        results: List[ResearchResult] = []
        for paper in client.results(search):
            # Convert published date to string
            published_date = paper.published.strftime("%Y-%m-%d")

            # Apply date filtering if specified
            if date_from and published_date < date_from:
                continue
            if date_to and published_date > date_to:
                continue

            # Extract authors
            authors = [author.name for author in paper.authors]

            # Create ResearchResult
            result = ResearchResult(
                title=paper.title,
                abstract=paper.summary.replace("\n", " ").strip(),
                url=paper.entry_id,
                published_date=published_date,
                source="arxiv",
                authors=authors,
            )
            results.append(result)

        return results

    except Exception as e:
        raise Exception(f"Failed to search arXiv: {str(e)}")
