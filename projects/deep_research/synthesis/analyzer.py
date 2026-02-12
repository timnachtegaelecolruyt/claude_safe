"""LLM-powered research synthesis using local Ollama models."""

from typing import Dict, List, Any
from openai import OpenAI
from ..models import ResearchQuery, ResearchResult
from ..config import config


def analyze_research(query: ResearchQuery, results: List[ResearchResult]) -> Dict[str, Any]:
    """
    Analyze research results and generate insights using local Ollama models.

    Args:
        query: Original research query
        results: List of research results from various sources

    Returns:
        Dictionary with 'summary' and 'insights' keys

    Raises:
        Exception: If the Ollama API request fails
    """
    if not results:
        return {
            "summary": f"No research results found for the topic: {query.topic}",
            "insights": ["No data available for analysis"],
        }

    try:
        # Build context from research results
        context = _build_research_context(results)

        # Create prompt for analysis
        prompt = f"""You are a research analyst tasked with synthesizing insights from academic papers and sources.

Research Topic: {query.topic}

I have collected {len(results)} research papers and sources on this topic. Please analyze them and provide:

1. **Executive Summary**: A concise 2-3 paragraph overview of the current state of research in this area
2. **Key Insights**: 5-7 specific, actionable insights or trends you observe from this research
3. **Notable Findings**: Any particularly interesting or significant findings that stand out

Research Papers:

{context}

Please provide your analysis in a clear, structured format."""

        # Call Ollama API
        response_text = _call_ollama(prompt)

        # Parse response into structured format
        parsed = _parse_response(response_text)

        return parsed

    except Exception as e:
        raise Exception(f"Failed to analyze research with LLM: {str(e)}")


def _call_ollama(prompt: str) -> str:
    """Call Ollama API with the given prompt using OpenAI-compatible interface."""
    client = OpenAI(
        base_url=config.ollama_base_url,
        api_key=config.ollama_api_key,
    )

    response = client.chat.completions.create(
        model=config.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
    )

    # Add error handling for empty responses
    if not response.choices:
        raise ValueError("Ollama API returned no choices in response")

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Ollama API returned empty content")

    return content


def _build_research_context(results: List[ResearchResult]) -> str:
    """Build formatted context string from research results."""
    context_parts = []

    for idx, result in enumerate(results, 1):
        authors_str = ", ".join(result.authors[:3]) if result.authors else "Unknown"
        if len(result.authors) > 3:
            authors_str += " et al."

        context_parts.append(
            f"""
Paper {idx}:
Title: {result.title}
Authors: {authors_str}
Date: {result.published_date}
Source: {result.source}
Abstract: {result.abstract[:500]}...
URL: {result.url}
""".strip()
        )

    return "\n\n---\n\n".join(context_parts)


def _parse_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM response into structured format with robust fallback.

    This parser tries structured parsing first, then falls back to
    paragraph-based extraction if no section headers are found.
    """
    lines = response_text.split("\n")
    summary_lines: List[str] = []
    insights: List[str] = []
    current_section = None

    # Try structured parsing first
    for line in lines:
        line = line.strip()

        # Detect section headers
        if "executive summary" in line.lower() or "summary" in line.lower():
            current_section = "summary"
            continue
        elif "key insights" in line.lower() or "insights" in line.lower():
            current_section = "insights"
            continue
        elif "notable findings" in line.lower():
            current_section = "insights"
            continue

        # Skip empty lines and headers
        if not line or line.startswith("#"):
            continue

        # Collect content based on current section
        if current_section == "summary" and line:
            summary_lines.append(line)
        elif current_section == "insights" and line:
            # Remove bullet points and numbering
            cleaned = line.lstrip("•-*123456789. ")
            if cleaned and len(cleaned) > 10:  # Minimum length check
                insights.append(cleaned)

    # Enhanced fallback logic if parsing failed
    if not summary_lines and not insights:
        # Split by paragraphs and take first as summary, rest as insights
        paragraphs = [p.strip() for p in response_text.split("\n\n") if p.strip()]
        if paragraphs:
            summary_lines = [paragraphs[0]]
            # Extract bullet-like lines as insights
            for para in paragraphs[1:]:
                lines_in_para = para.split("\n")
                for line in lines_in_para:
                    cleaned = line.strip().lstrip("•-*123456789. ")
                    if cleaned and len(cleaned) > 20:
                        insights.append(cleaned)

    # Build final output
    summary = " ".join(summary_lines) if summary_lines else response_text[:800] + "..."
    if not insights:
        insights = ["Analysis provided in summary"]

    return {"summary": summary, "insights": insights[:10]}  # Limit to 10 insights
