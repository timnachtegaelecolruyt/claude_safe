"""Google Trends integration for market interest and trend analysis."""

from typing import List, Optional
from ..models import ResearchResult


def search_trends(
    topic: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_results: int = 10,
) -> List[ResearchResult]:
    """
    Search Google Trends for interest data and related queries.

    Returns trend data as ResearchResult objects including:
    - Interest over time summary
    - Top related queries
    - Rising related queries

    Args:
        topic: Search query string
        date_from: Start date for filtering (YYYY-MM-DD format, optional)
        date_to: End date for filtering (YYYY-MM-DD format, optional)
        max_results: Maximum number of results to return

    Returns:
        List of ResearchResult objects with source="google_trends"

    Raises:
        Exception: If the Google Trends API request fails
    """
    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 30))

        # Build timeframe from dates
        timeframe = _build_timeframe(date_from, date_to)

        # Truncate topic to fit Google Trends keyword limit (max ~100 chars)
        keyword = topic[:100]

        pytrends.build_payload(
            kw_list=[keyword],
            timeframe=timeframe,
            geo="",
        )

        results: List[ResearchResult] = []

        # 1. Interest over time summary
        try:
            interest_df = pytrends.interest_over_time()
            if not interest_df.empty and keyword in interest_df.columns:
                series = interest_df[keyword]
                avg_interest = series.mean()
                max_interest = series.max()
                min_interest = series.min()
                latest = series.iloc[-1] if len(series) > 0 else 0

                # Detect trend direction
                if len(series) >= 4:
                    first_quarter = series.iloc[: len(series) // 4].mean()
                    last_quarter = series.iloc[-len(series) // 4 :].mean()
                    if last_quarter > first_quarter * 1.2:
                        direction = "Rising"
                    elif last_quarter < first_quarter * 0.8:
                        direction = "Declining"
                    else:
                        direction = "Stable"
                else:
                    direction = "Insufficient data"

                abstract = (
                    f"Google Trends interest over time for '{keyword}'. "
                    f"Trend: {direction}. "
                    f"Current interest: {latest}/100. "
                    f"Average: {avg_interest:.0f}/100. "
                    f"Peak: {max_interest}/100. Low: {min_interest}/100. "
                    f"Period: {interest_df.index[0].strftime('%Y-%m-%d')} to "
                    f"{interest_df.index[-1].strftime('%Y-%m-%d')}."
                )

                trends_url = f"https://trends.google.com/trends/explore?q={keyword.replace(' ', '+')}"

                results.append(
                    ResearchResult(
                        title=f"Google Trends: Interest over time for '{keyword}'",
                        abstract=abstract,
                        url=trends_url,
                        published_date=interest_df.index[-1].strftime("%Y-%m-%d"),
                        source="google_trends",
                        authors=[],
                    )
                )
        except Exception:
            pass  # Interest over time may fail for niche topics

        # 2. Related queries (top and rising)
        try:
            related = pytrends.related_queries()
            if keyword in related:
                keyword_data = related[keyword]

                # Top related queries
                top_df = keyword_data.get("top")
                if top_df is not None and not top_df.empty:
                    for _, row in top_df.head(max_results // 2).iterrows():
                        query_text = row.get("query", "")
                        value = row.get("value", 0)
                        if not query_text:
                            continue

                        results.append(
                            ResearchResult(
                                title=f"Related query: {query_text}",
                                abstract=(
                                    f"Top related Google Trends query for '{keyword}'. "
                                    f"Relative interest score: {value}/100."
                                ),
                                url=f"https://trends.google.com/trends/explore?q={query_text.replace(' ', '+')}",
                                published_date="",
                                source="google_trends",
                                authors=[],
                            )
                        )

                # Rising related queries
                rising_df = keyword_data.get("rising")
                if rising_df is not None and not rising_df.empty:
                    for _, row in rising_df.head(max_results // 2).iterrows():
                        query_text = row.get("query", "")
                        value = row.get("value", "")
                        if not query_text:
                            continue

                        # Value can be "Breakout" or a percentage
                        value_str = f"{value}% increase" if isinstance(value, (int, float)) else str(value)

                        results.append(
                            ResearchResult(
                                title=f"Rising query: {query_text}",
                                abstract=(
                                    f"Rising Google Trends query for '{keyword}'. "
                                    f"Growth: {value_str}. "
                                    f"This indicates growing market interest in this area."
                                ),
                                url=f"https://trends.google.com/trends/explore?q={query_text.replace(' ', '+')}",
                                published_date="",
                                source="google_trends",
                                authors=[],
                            )
                        )
        except Exception:
            pass  # Related queries may fail for niche topics

        # 3. Related topics
        try:
            related_topics = pytrends.related_topics()
            if keyword in related_topics:
                keyword_topics = related_topics[keyword]

                rising_topics = keyword_topics.get("rising")
                if rising_topics is not None and not rising_topics.empty:
                    remaining = max_results - len(results)
                    for _, row in rising_topics.head(max(remaining, 3)).iterrows():
                        topic_title = row.get("topic_title", "")
                        topic_type = row.get("topic_type", "")
                        value = row.get("value", "")
                        if not topic_title:
                            continue

                        value_str = f"{value}% increase" if isinstance(value, (int, float)) else str(value)

                        results.append(
                            ResearchResult(
                                title=f"Rising topic: {topic_title}",
                                abstract=(
                                    f"Rising Google Trends topic related to '{keyword}'. "
                                    f"Type: {topic_type}. Growth: {value_str}."
                                ),
                                url=f"https://trends.google.com/trends/explore?q={topic_title.replace(' ', '+')}",
                                published_date="",
                                source="google_trends",
                                authors=[],
                            )
                        )
        except Exception:
            pass  # Related topics may fail for niche topics

        return results[:max_results]

    except Exception as e:
        raise Exception(f"Failed to fetch Google Trends data: {e}")


def _build_timeframe(date_from: Optional[str], date_to: Optional[str]) -> str:
    """Convert date range to pytrends timeframe format."""
    if date_from and date_to:
        return f"{date_from} {date_to}"
    elif date_from:
        # From date to now
        from datetime import datetime

        today = datetime.now().strftime("%Y-%m-%d")
        return f"{date_from} {today}"
    else:
        # Default: last 12 months
        return "today 12-m"
