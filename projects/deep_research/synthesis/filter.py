"""AI-powered relevance filtering for research results using Ollama."""

import json
from typing import List, Dict
from openai import OpenAI
from ..models import ResearchQuery, ResearchResult
from ..config import config


def filter_relevant_results(
    query: ResearchQuery, results: List[ResearchResult], verbose: bool = True
) -> tuple[List[ResearchResult], Dict[str, int]]:
    """
    Filter research results for relevance using Ollama as an AI judge.

    Args:
        query: Original research query
        results: List of all research results to filter
        verbose: Whether to print filtering progress

    Returns:
        Tuple of (filtered_results, statistics)
        - filtered_results: List of relevant research results
        - statistics: Dict with 'total', 'relevant', 'filtered_out' counts
    """
    if not results:
        return [], {"total": 0, "relevant": 0, "filtered_out": 0}

    if verbose:
        print(f"      Filtering {len(results)} results for relevance...")

    relevant_results = []
    filtered_out = 0
    filtered_reasons = []

    for idx, result in enumerate(results, 1):
        is_relevant, reason = _judge_relevance(query.topic, result)

        if is_relevant:
            relevant_results.append(result)
            if verbose:
                print(f"      ✓ KEPT: {result.title[:60]}... ({reason})")
        else:
            filtered_out += 1
            filtered_reasons.append((result.title[:60], reason))
            if verbose:
                print(f"      ✗ FILTERED: {result.title[:60]}... ({reason})")

    stats = {"total": len(results), "relevant": len(relevant_results), "filtered_out": filtered_out}

    if verbose:
        print(f"\n      Filtering complete: {stats['relevant']}/{stats['total']} results retained")

    return relevant_results, stats


def _judge_relevance(topic: str, result: ResearchResult) -> tuple[bool, str]:
    """
    Use Ollama to judge if a single research result is relevant to the topic.

    Args:
        topic: The research topic
        result: A single research result to evaluate

    Returns:
        Tuple of (is_relevant, reason)
    """
    try:
        prompt = f"""You are a research relevance judge. Your task is to determine if a research paper \
or article is relevant to a specific research topic.

Research Topic: {topic}

Paper/Article to Evaluate:
Title: {result.title}
Abstract: {result.abstract[:800]}
Source: {result.source}

Question: Is this paper/article directly relevant to the research topic?

Rules for judging relevance:
1. The paper should discuss concepts, methods, or applications directly related to the topic
2. Be lenient with industry news and practical tools - these are often highly relevant even if \
not academic
3. Papers from completely different domains (astronomy, biology, physics) are NOT relevant unless \
they directly apply to the topic
4. For academic papers, the topic's key terms should appear meaningfully
5. For news/web articles about tools, companies, or practices in the field, be more permissive

Respond with ONLY a JSON object in this exact format:
{{"relevant": true/false, "reason": "brief explanation in one sentence"}}

Your response:"""

        response_text = _call_ollama_judge(prompt)

        # Parse JSON response
        try:
            # Try to extract JSON from response
            response_text = response_text.strip()
            if "```json" in response_text:
                # Extract from code block
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                response_text = response_text[start:end]

            judgment = json.loads(response_text)
            return judgment.get("relevant", False), judgment.get("reason", "No reason provided")

        except json.JSONDecodeError:
            # Fallback: look for true/false keywords
            lower_response = response_text.lower()
            if "true" in lower_response or '"relevant": true' in lower_response:
                return True, "Keyword match fallback"
            return False, "Keyword match fallback"

    except Exception as e:
        # On error, default to keeping the result (conservative approach)
        print(f"      Warning: Failed to judge relevance for '{result.title}': {e}")
        return True, f"Error: {str(e)}"


def _call_ollama_judge(prompt: str) -> str:
    """Call Ollama API for relevance judgment."""
    client = OpenAI(
        base_url=config.ollama_base_url,
        api_key=config.ollama_api_key,
    )

    response = client.chat.completions.create(
        model=config.ollama_model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,  # Short response needed
        temperature=0.1,  # Low temperature for more consistent judgments
    )

    if not response.choices:
        raise ValueError("Ollama API returned no choices in response")

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Ollama API returned empty content")

    return content
