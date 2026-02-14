"""AI-powered query rewriting for better search results using Ollama."""

import json
from openai import OpenAI
from ..config import config


def rewrite_query(topic: str, verbose: bool = True) -> str:
    """
    Use Ollama to rewrite a research topic into an optimized search query.

    The LLM expands the topic with synonyms, clarifying terms, and exclusions
    to improve search precision across academic and web sources.

    Args:
        topic: Original research topic from the user
        verbose: Whether to print progress

    Returns:
        Rewritten search query string optimized for source APIs
    """
    if verbose:
        print("      Rewriting query for better search precision...")

    prompt = f"""You are a search query optimizer. Your task is to rewrite a research topic into a \
better search query that will return relevant results from academic databases and web search engines.

Original topic: {topic}

Instructions:
1. Identify the core research intent (e.g., market analysis, technical overview, academic survey)
2. Add 2-3 key synonyms or related terms that improve recall
3. Add exclusion terms (prefixed with -) to filter out irrelevant results (e.g., -resume -job -hiring \
if the topic is about market research, not job listings)
4. Keep the query concise — no more than 15 words total (excluding exclusion terms)
5. Do NOT add quotes unless searching for an exact phrase is critical
6. Optimize for precision: a focused query is better than a broad one

Respond with ONLY a JSON object in this exact format:
{{"query": "your optimized search query here", "reasoning": "brief explanation of changes"}}

Your response:"""

    try:
        client = OpenAI(
            base_url=config.ollama_base_url,
            api_key=config.ollama_api_key,
        )

        response = client.chat.completions.create(
            model=config.ollama_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3,
        )

        if not response.choices:
            raise ValueError("Ollama API returned no choices")

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Ollama API returned empty content")

        # Parse JSON response
        content = content.strip()
        if "```json" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            content = content[start:end]

        result = json.loads(content)
        rewritten = result.get("query", topic)
        reasoning = result.get("reasoning", "")

        if verbose:
            print(f"      Original:  {topic}")
            print(f"      Rewritten: {rewritten}")
            if reasoning:
                print(f"      Reasoning: {reasoning}")

        return rewritten

    except Exception as e:
        if verbose:
            print(f"      Warning: Query rewriting failed ({e}), using original topic")
        return topic
