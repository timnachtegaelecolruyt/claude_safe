"""AI-powered source selection for research queries using Ollama."""

import json
from typing import List, Dict, Tuple
from openai import OpenAI
from ..config import config


def select_sources(topic: str, available_sources: List[str], verbose: bool = True) -> Tuple[List[str], Dict[str, str]]:
    """
    Use Ollama to intelligently select the most appropriate sources for a research topic.

    Args:
        topic: The research topic
        available_sources: List of available source names
        verbose: Whether to print selection details

    Returns:
        Tuple of (selected_sources, reasoning_dict)
        - selected_sources: List of source names to use
        - reasoning_dict: Dict mapping source name to reason for selection/exclusion
    """
    if not available_sources:
        return [], {}

    if verbose:
        print("      Analyzing topic to select optimal sources...")

    try:
        # Build source descriptions
        source_descriptions = {
            "arxiv": (
                "Academic research papers in physics, computer science, mathematics, biology, and "
                "other sciences. Best for: fundamental research, algorithms, theoretical work, "
                "scientific discoveries."
            ),
            "semantic_scholar": (
                "Academic papers with citation data across all fields. Best for: research papers, "
                "academic citations, scholarly work, scientific studies."
            ),
            "news": (
                "Recent news articles, press releases, and industry announcements. Best for: "
                "current events, company news, product launches, industry trends, breaking developments."
            ),
            "web": (
                "General web content including blogs, documentation, tutorials, and technical articles. "
                "Best for: practical guides, tools documentation, best practices, how-tos, engineering blogs."
            ),
            "hackernews": (
                "Tech community discussions and curated links. Best for: trending tech topics, "
                "startup news, developer perspectives, community opinions, popular tools."
            ),
            "dblp": (
                "Comprehensive computer science bibliography covering journals, conferences, and "
                "workshops. Best for: computer science publications, conference papers, CS venues, "
                "author bibliographies."
            ),
            "openalex": (
                "Fully-open index of 474M+ scholarly works across all disciplines. Best for: "
                "broad academic search, interdisciplinary research, citation analysis, open access papers."
            ),
            "crossref": (
                "Metadata for 140M+ scholarly works from publishers worldwide including journals, "
                "books, and dissertations. Best for: published research across all fields, DOI lookup, "
                "publisher metadata, citation counts."
            ),
            "core": (
                "Aggregator of 300M+ open access research papers from repositories and journals. "
                "Best for: open access papers, institutional repository content, full-text access, "
                "interdisciplinary research."
            ),
            "europepmc": (
                "40M+ life sciences publications including PubMed and PubMed Central. Best for: "
                "biomedical research, medicine, biology, pharmacology, clinical studies, life sciences."
            ),
            "reddit": (
                "Community discussions, user experiences, and opinions across all topics. Best for: "
                "real-world experiences, tool comparisons, industry practices, community sentiment, "
                "product feedback, troubleshooting, market insights."
            ),
            "github": (
                "Open source repositories with stars, forks, and project metadata. Best for: "
                "open source tools, software projects, library adoption, code examples, "
                "technology landscape, developer tools, market research on OSS adoption."
            ),
            "google_trends": (
                "Google search interest data over time, related queries, and rising topics. Best for: "
                "market demand analysis, trend direction, emerging topics, seasonal patterns, "
                "competitive interest comparison, market research."
            ),
        }

        # Filter to only available sources
        descriptions = {src: desc for src, desc in source_descriptions.items() if src in available_sources}

        # Build prompt
        prompt = f"""You are a research source selection expert. Your task is to analyze a research topic and \
select the most appropriate sources to search.

Research Topic: {topic}

Available Sources:
{_format_source_descriptions(descriptions)}

Your task:
1. Analyze the research topic and determine what type of information would be most valuable
2. Select 3-7 sources that are most likely to have relevant, high-quality results
3. Consider the nature of the topic: academic, industry/practical, or mixed
4. Provide a brief reason for each selection

Rules:
- Select at least 3 sources (for redundancy and coverage)
- For industry or practical topics (tools, platforms, company practices, best practices),
  ALWAYS include "web" and "news" alongside academic sources
- For academic/scientific topics, prioritize academic sources but still consider "web" for practical context
- For mixed topics, use a broad selection from both academic and non-academic sources
- Don't select sources that are clearly irrelevant (e.g., europepmc for a pure computer science topic)
- When in doubt, include a source rather than exclude it

Respond with ONLY a JSON object in this exact format:
{{
  "selected": ["source1", "source2", ...],
  "reasoning": {{
    "source1": "reason for selection",
    "source2": "reason for selection",
    "excluded_source": "reason for exclusion"
  }}
}}

Your response:"""

        response_text = _call_ollama(prompt)

        # Parse JSON response
        try:
            response_text = response_text.strip()
            if "```json" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                response_text = response_text[start:end]

            result = json.loads(response_text)
            selected = result.get("selected", [])
            reasoning = result.get("reasoning", {})

            # Validate selected sources
            selected = [s for s in selected if s in available_sources]

            # Ensure at least 3 sources
            if len(selected) < 3 and len(available_sources) >= 3:
                if verbose:
                    print("      Warning: LLM selected <3 sources, using all available sources as fallback")
                return available_sources, {"fallback": "LLM selected too few sources"}

            if verbose:
                print(f"      Selected {len(selected)}/{len(available_sources)} sources: {', '.join(selected)}")
                for source in selected:
                    if source in reasoning:
                        print(f"        • {source}: {reasoning[source]}")

            return selected, reasoning

        except json.JSONDecodeError as e:
            if verbose:
                print(f"      Warning: Failed to parse LLM response, using all sources: {e}")
            return available_sources, {"error": "JSON parse failed"}

    except Exception as e:
        if verbose:
            print(f"      Warning: Source selection failed, using all sources: {e}")
        return available_sources, {"error": str(e)}


def _format_source_descriptions(descriptions: Dict[str, str]) -> str:
    """Format source descriptions for the prompt."""
    lines = []
    for source, desc in descriptions.items():
        lines.append(f"- **{source}**: {desc}")
    return "\n".join(lines)


def _call_ollama(prompt: str) -> str:
    """Call Ollama API for source selection."""
    client = OpenAI(
        base_url=config.ollama_base_url,
        api_key=config.ollama_api_key,
    )

    response = client.chat.completions.create(
        model=config.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.2,  # Low temperature for more consistent decisions
    )

    if not response.choices:
        raise ValueError("Ollama API returned no choices in response")

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Ollama API returned empty content")

    return content
