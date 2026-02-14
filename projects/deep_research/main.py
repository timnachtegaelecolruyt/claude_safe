"""CLI entry point for the deep research automation tool."""

import argparse
import sys
from typing import List

from .models import ResearchQuery, ResearchReport, ResearchResult
from .sources.arxiv_source import search_papers as arxiv_search
from .sources.web_source import search_web, search_news
from .sources.scholar_source import search_papers as scholar_search
from .sources.hackernews_source import search_stories
from .sources.openalex_source import search_papers as openalex_search
from .sources.dblp_source import search_papers as dblp_search
from .sources.europepmc_source import search_papers as europepmc_search
from .synthesis.analyzer import analyze_research
from .synthesis.filter import filter_relevant_results
from .synthesis.source_selector import select_sources
from .report_generator import generate_markdown, save_report
from .config import config

ALL_SOURCES = ["arxiv", "openalex", "dblp", "europepmc", "web", "news", "semantic_scholar", "hackernews"]


def _collect_results(query: ResearchQuery, active_sources: List[str]) -> List[ResearchResult]:
    """Collect results from all active sources, handling failures gracefully."""
    all_results: List[ResearchResult] = []
    total = len(active_sources)

    for idx, source in enumerate(active_sources, 1):
        try:
            if source == "arxiv":
                print(f"  [{idx}/{total}] Searching arXiv...")
                results = arxiv_search(
                    topic=query.topic,
                    date_from=query.date_from,
                    date_to=query.date_to,
                    max_results=query.max_results,
                )
            elif source == "openalex":
                print(f"  [{idx}/{total}] Searching OpenAlex...")
                results = openalex_search(
                    topic=query.topic,
                    date_from=query.date_from,
                    date_to=query.date_to,
                    max_results=query.max_results,
                )
            elif source == "dblp":
                print(f"  [{idx}/{total}] Searching DBLP...")
                results = dblp_search(
                    topic=query.topic,
                    date_from=query.date_from,
                    date_to=query.date_to,
                    max_results=query.max_results,
                )
            elif source == "europepmc":
                print(f"  [{idx}/{total}] Searching Europe PMC...")
                results = europepmc_search(
                    topic=query.topic,
                    date_from=query.date_from,
                    date_to=query.date_to,
                    max_results=query.max_results,
                )
            elif source == "web":
                print(f"  [{idx}/{total}] Searching web (DuckDuckGo)...")
                results = search_web(topic=query.topic, max_results=query.max_results)
            elif source == "news":
                print(f"  [{idx}/{total}] Searching news (DuckDuckGo)...")
                results = search_news(topic=query.topic, max_results=query.max_results)
            elif source == "semantic_scholar":
                print(f"  [{idx}/{total}] Searching Semantic Scholar...")
                results = scholar_search(
                    topic=query.topic,
                    date_from=query.date_from,
                    date_to=query.date_to,
                    max_results=query.max_results,
                )
            elif source == "hackernews":
                print(f"  [{idx}/{total}] Searching HackerNews...")
                results = search_stories(topic=query.topic, max_results=query.max_results)
            else:
                print(f"  [{idx}/{total}] Unknown source '{source}', skipping")
                continue

            print(f"         Found {len(results)} results")
            all_results.extend(results)

        except Exception as e:
            print(f"         WARNING: {source} failed: {e}", file=sys.stderr)

    return all_results


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Deep Research Automation Tool - Automated research synthesis using local LLMs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m projects.deep_research.main --topic "quantum computing"
  python -m projects.deep_research.main --topic "machine learning" --max-results 20
  python -m projects.deep_research.main --topic "kubernetes adoption" --exclude-source hackernews,news
        """,
    )

    parser.add_argument("--topic", type=str, required=True, help="Research topic or query")
    parser.add_argument("--date-from", type=str, default=None, help="Start date for filtering (YYYY-MM-DD)")
    parser.add_argument("--date-to", type=str, default=None, help="End date for filtering (YYYY-MM-DD)")
    parser.add_argument(
        "--max-results",
        type=int,
        default=config.max_results,
        help=f"Maximum results per source (default: {config.max_results})",
    )
    parser.add_argument("--output", type=str, default=None, help="Custom output filename")
    parser.add_argument(
        "--exclude-source",
        type=str,
        default=None,
        help=f"Comma-separated sources to exclude (available: {','.join(ALL_SOURCES)})",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Disable AI relevance filtering (keeps all results)",
    )
    parser.add_argument(
        "--no-source-selection",
        action="store_true",
        help="Disable AI source selection (uses all configured sources)",
    )

    args = parser.parse_args()

    # Determine active sources
    active_sources = [s for s in config.enabled_sources if s in ALL_SOURCES]
    if args.exclude_source:
        excluded = {s.strip() for s in args.exclude_source.split(",")}
        active_sources = [s for s in active_sources if s not in excluded]

    if not active_sources:
        print("Error: No sources enabled. Check --exclude-source and ENABLED_SOURCES.", file=sys.stderr)
        sys.exit(1)

    # AI-powered source selection (optional)
    enable_selection = config.enable_source_selection and not args.no_source_selection
    if enable_selection:
        print(f"\n{'='*60}")
        print("Deep Research Tool - Starting Analysis")
        print(f"{'='*60}\n")
        print("[0/5] Selecting optimal sources using AI...")
        selected_sources, reasoning = select_sources(args.topic, active_sources, verbose=True)
        active_sources = selected_sources
        print()

    try:
        # Print banner if not already printed by source selection
        if not enable_selection:
            print(f"\n{'='*60}")
            print("Deep Research Tool - Starting Analysis")
            print(f"{'='*60}\n")

        print(f"Topic: {args.topic}")
        print(f"Max Results: {args.max_results} per source")
        print(f"Sources: {', '.join(active_sources)}")
        if args.date_from:
            print(f"Date From: {args.date_from}")
        if args.date_to:
            print(f"Date To: {args.date_to}")
        print()

        query = ResearchQuery(
            topic=args.topic, date_from=args.date_from, date_to=args.date_to, max_results=args.max_results
        )

        # Step 1: Collect from all sources
        step_num = "[1/5]" if enable_selection else "[1/4]"
        print(f"{step_num} Gathering results from sources...")
        results = _collect_results(query, active_sources)
        print(f"\n      Total: {len(results)} results from {len(active_sources)} sources\n")

        if not results:
            print("No results found. Try a different topic or date range.")
            sys.exit(1)

        # Step 2: Filter for relevance (optional)
        enable_filter = config.enable_relevance_filter and not args.no_filter
        if enable_filter:
            step_num = "[2/5]" if enable_selection else "[2/4]"
            print(f"{step_num} Filtering results for relevance using Ollama ({config.ollama_model})...")
            results, filter_stats = filter_relevant_results(query, results, verbose=True)
            print(
                f"\n      Filtered: {filter_stats['filtered_out']} irrelevant, "
                f"{filter_stats['relevant']} relevant results retained\n"
            )

            if not results:
                print("No relevant results found after filtering. Try a different topic or use --no-filter.")
                sys.exit(1)
        else:
            step_num = "[2/5]" if enable_selection else "[2/4]"
            print(f"{step_num} Skipping relevance filtering (disabled)\n")

        # Step 3: Analyze with Ollama
        # Calculate step numbers based on enabled features
        total_steps = 3  # Base: collect, analyze, save
        if enable_selection:
            total_steps += 1
        if enable_filter:
            total_steps += 1

        current_step = 2 if enable_selection else 1
        current_step += 1 if enable_filter else 0

        print(f"[{current_step}/{total_steps}] Analyzing research with Ollama ({config.ollama_model})...")
        analysis = analyze_research(query, results)
        print(f"      Generated {len(analysis['insights'])} insights\n")

        # Step 4: Create and save report
        current_step += 1
        print(f"[{current_step}/{total_steps}] Generating and saving report...")
        report = ResearchReport(
            query=query, summary=analysis["summary"], insights=analysis["insights"], results=results
        )

        markdown = generate_markdown(report)
        filepath = save_report(markdown, filename=args.output)
        print(f"      Saved to: {filepath}\n")

        print(f"{'='*60}")
        print("Research analysis complete!")
        print(f"{'='*60}\n")

        # Print summary
        source_counts = {}
        for r in results:
            source_counts[r.source] = source_counts.get(r.source, 0) + 1

        print("Summary:")
        print(f"- Total results: {len(results)}")
        for src, count in source_counts.items():
            print(f"  - {src}: {count}")
        print(f"- Key insights: {len(analysis['insights'])}")
        print(f"- Report: {filepath}")
        print()

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
