"""CLI entry point for the deep research automation tool."""

import argparse
import sys

from .models import ResearchQuery, ResearchReport
from .sources.arxiv_source import search_papers
from .synthesis.analyzer import analyze_research
from .report_generator import generate_markdown, save_report
from .config import config


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Deep Research Automation Tool - Automated research synthesis using Claude AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m projects.deep_research.main --topic "quantum computing"
  python -m projects.deep_research.main --topic "machine learning" --max-results 20
  python -m projects.deep_research.main --topic "climate change" --date-from 2024-01-01
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

    args = parser.parse_args()

    try:
        # Create research query
        print(f"\n{'='*60}")
        print("Deep Research Tool - Starting Analysis")
        print(f"{'='*60}\n")
        print(f"Topic: {args.topic}")
        print(f"Max Results: {args.max_results}")
        if args.date_from:
            print(f"Date From: {args.date_from}")
        if args.date_to:
            print(f"Date To: {args.date_to}")
        print()

        query = ResearchQuery(
            topic=args.topic, date_from=args.date_from, date_to=args.date_to, max_results=args.max_results
        )

        # Step 1: Fetch from arXiv
        print("[1/4] Searching arXiv for papers...")
        results = search_papers(
            topic=query.topic,
            date_from=query.date_from,
            date_to=query.date_to,
            max_results=query.max_results,
        )
        print(f"      Found {len(results)} papers\n")

        if not results:
            print("No results found. Try a different topic or date range.")
            sys.exit(1)

        # Step 2: Analyze with Ollama
        print(f"[2/4] Analyzing research with Ollama ({config.ollama_model})...")
        analysis = analyze_research(query, results)
        print(f"      Generated {len(analysis['insights'])} insights\n")

        # Step 3: Create report
        print("[3/4] Generating research report...")
        report = ResearchReport(
            query=query, summary=analysis["summary"], insights=analysis["insights"], results=results
        )

        markdown = generate_markdown(report)
        print("      Report generated\n")

        # Step 4: Save to file
        print("[4/4] Saving report to file...")
        filepath = save_report(markdown, filename=args.output)
        print(f"      Saved to: {filepath}\n")

        print(f"{'='*60}")
        print("Research analysis complete!")
        print(f"{'='*60}\n")

        # Print summary
        print("Quick Summary:")
        print(f"- Papers analyzed: {len(results)}")
        print(f"- Key insights: {len(analysis['insights'])}")
        print(f"- Report location: {filepath}")
        print()

    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
