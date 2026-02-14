"""Data models for the deep research automation tool."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ResearchQuery(BaseModel):
    """Input specification for a research request."""

    topic: str = Field(..., description="Research topic or query string")
    search_query: Optional[str] = Field(None, description="AI-rewritten search query optimized for source APIs")
    date_from: Optional[str] = Field(None, description="Start date for filtering results (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="End date for filtering results (YYYY-MM-DD)")
    max_results: int = Field(10, ge=1, le=100, description="Maximum number of results to fetch per source")

    @property
    def effective_query(self) -> str:
        """Return search_query if available, otherwise fall back to topic."""
        return self.search_query or self.topic

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "topic": "quantum computing error correction",
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
                "max_results": 10,
            }
        }
    )


class ResearchResult(BaseModel):
    """Raw data from a single research source."""

    title: str = Field(..., description="Title of the research paper, article, or resource")
    abstract: str = Field(..., description="Abstract, summary, or main content")
    url: str = Field(..., description="URL to the original resource")
    published_date: str = Field(..., description="Publication date (YYYY-MM-DD format)")
    source: str = Field(..., description="Source identifier (e.g., 'arxiv', 'web', 'news')")
    authors: Optional[List[str]] = Field(default_factory=list, description="List of authors")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Quantum Error Correction with Surface Codes",
                "abstract": "We present a novel approach to quantum error correction...",
                "url": "https://arxiv.org/abs/2401.12345",
                "published_date": "2024-01-15",
                "source": "arxiv",
                "authors": ["John Doe", "Jane Smith"],
            }
        }
    )


class ResearchReport(BaseModel):
    """Final research report with synthesized insights."""

    query: ResearchQuery = Field(..., description="Original research query")
    summary: str = Field(..., description="Executive summary of findings")
    insights: List[str] = Field(default_factory=list, description="Key insights and trends")
    results: List[ResearchResult] = Field(default_factory=list, description="Raw research results")
    generated_at: datetime = Field(default_factory=datetime.now, description="Report generation timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": {"topic": "quantum computing", "max_results": 10},
                "summary": "Recent advances in quantum computing focus on...",
                "insights": ["Trend 1: Error correction improvements", "Trend 2: Scalability challenges"],
                "results": [],
                "generated_at": "2024-01-15T10:30:00",
            }
        }
    )
