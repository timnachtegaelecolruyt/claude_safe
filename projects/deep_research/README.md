# Deep Research Automation Tool

A Python-based research automation tool that searches academic papers, synthesizes insights using local Ollama models, and generates comprehensive Markdown reports.

## Features

- **Multi-Source Research**: Searches 13 sources including arXiv, Semantic Scholar, OpenAlex, DBLP, CrossRef, CORE, Europe PMC, Reddit, GitHub, Google Trends, web, news, and HackerNews
- **AI Source Selection**: Automatically selects the most relevant sources for each topic
- **AI Relevance Filtering**: Uses Ollama to automatically filter out irrelevant papers/articles
- **AI-Powered Synthesis**: Uses local Ollama models to analyze and extract key insights
- **Markdown Reports**: Generates well-formatted, readable research reports
- **Simple CLI**: Easy-to-use command-line interface
- **Configurable**: Customizable search parameters and date ranges
- **Local & Private**: Runs entirely with local LLM models via Ollama

## What This Tool Does

The Deep Research Tool automates the research process:

1. **Analyzes** the topic and selects optimal sources (optional, enabled by default)
2. **Searches** selected sources (arXiv, OpenAlex, DBLP, Europe PMC, CORE, CrossRef, Semantic Scholar, Reddit, GitHub, Google Trends, web, news, HackerNews) for papers and articles
3. **Filters** results using AI to remove irrelevant content (optional, enabled by default)
4. **Collects** paper metadata, abstracts, and citations
5. **Analyzes** the research using local Ollama models to identify trends and insights
6. **Generates** a comprehensive Markdown report with:
   - Executive summary
   - Key insights and trends
   - Full paper details with links
   - Formatted citations

## Installation

### Prerequisites

- Python 3.10 or higher
- Ollama installed and running locally ([Download Ollama](https://ollama.ai))
- At least one Ollama model pulled (e.g., `ollama pull llama3.2`)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/deep-research.git
   cd deep-research
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # Or for development:
   pip install -e ".[dev]"
   ```

4. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

5. **Pull a model** (if you haven't already):
   ```bash
   ollama pull llama3.2
   ```

6. **Configure your environment**:
   ```bash
   cp .env.example .env
   ```

7. **Edit `.env` and configure Ollama settings**:
   ```
   OLLAMA_BASE_URL=http://localhost:11434/v1
   OLLAMA_API_KEY=ollama-local
   OLLAMA_MODEL=llama3.2
   ```

## Usage

### Basic Usage

```bash
python -m deep_research.main --topic "quantum computing"
```

Or if installed as a package:

```bash
deep-research --topic "quantum computing"
```

### Advanced Options

```bash
# Specify maximum number of results
python -m deep_research.main --topic "machine learning" --max-results 20

# Filter by date range
python -m deep_research.main --topic "climate change" --date-from 2024-01-01 --date-to 2024-12-31

# Custom output filename
python -m deep_research.main --topic "artificial intelligence" --output my_research.md
```

### Command-Line Arguments

- `--topic` (required): Research topic or query string
- `--max-results` (optional): Maximum number of papers to fetch per source (default: 10)
- `--date-from` (optional): Start date for filtering papers (YYYY-MM-DD)
- `--date-to` (optional): End date for filtering papers (YYYY-MM-DD)
- `--output` (optional): Custom output filename
- `--no-source-selection` (optional): Disable AI source selection (uses all configured sources)
- `--no-filter` (optional): Disable AI relevance filtering (keeps all results)
- `--exclude-source` (optional): Comma-separated sources to exclude (e.g., "hackernews,news")

## Output

Reports are saved to the `outputs/` directory with timestamped filenames:

```
outputs/research_report_20240115_143022.md
```

Each report includes:

- **Research Query**: Topic and search parameters
- **Executive Summary**: AI-generated overview of findings
- **Key Insights**: 5-7 specific trends or observations
- **Research Papers**: Full details of each paper found
  - Title, authors, publication date
  - Abstract
  - Source URL

## Example

```bash
$ python -m deep_research.main --topic "quantum error correction" --max-results 5

============================================================
Deep Research Tool - Starting Analysis
============================================================

Topic: quantum error correction
Max Results: 5

[1/4] Searching arXiv for papers...
      Found 5 papers

[2/4] Analyzing research with Ollama...
      Generated 6 insights

[3/4] Generating research report...
      Report generated

[4/4] Saving report to file...
      Saved to: outputs/research_report_20240115_143022.md

============================================================
Research analysis complete!
============================================================

Quick Summary:
- Papers analyzed: 5
- Key insights: 6
- Report location: outputs/research_report_20240115_143022.md
```

## AI Source Selection

The tool intelligently selects which sources to search based on your topic, saving time and improving result quality. Each source has specific strengths:

- **arXiv**: Academic research papers in physics, computer science, mathematics, biology, and other sciences
- **Semantic Scholar**: Academic papers with citation data across all fields
- **OpenAlex**: Fully-open index of 474M+ scholarly works across all disciplines
- **DBLP**: Comprehensive computer science bibliography covering journals, conferences, and workshops
- **CrossRef**: Metadata for 140M+ scholarly works from publishers worldwide
- **CORE**: Aggregator of 300M+ open access research papers from repositories and journals
- **Europe PMC**: 40M+ life sciences publications including PubMed and PubMed Central
- **news**: Recent news articles, press releases, and industry announcements
- **web**: General web content including blogs, documentation, tutorials, and technical articles
- **Reddit**: Community discussions, real-world experiences, and user opinions across all topics
- **GitHub**: Open source repositories with stars, forks, and project metadata
- **Google Trends**: Search interest over time, related queries, and rising topics for market analysis
- **hackernews**: Tech community discussions and curated links

**Example output:**
```
[0/5] Selecting optimal sources using AI...
      Analyzing topic to select optimal sources...
      Selected 3/10 sources: news, web, semantic_scholar
        • news: Industry topic likely to have recent announcements
        • web: Practical tooling information available
        • semantic_scholar: May have relevant research papers

[1/5] Gathering results from sources...
```

**Benefits:**
- **Faster execution** - Skips irrelevant sources (saves 20-40% of time)
- **Better quality results** - Searches only where relevant content exists
- **Higher relevance** - Fewer irrelevant results to filter out

**Examples:**
```bash
# Industry topic → auto-selects: news, web, semantic_scholar (skips arXiv)
python -m deep_research.main --topic "data platform metadata management"

# Academic topic → auto-selects: arxiv, semantic_scholar (may skip news)
python -m deep_research.main --topic "quantum error correction algorithms"

# Disable source selection and use all sources
python -m deep_research.main --topic "your topic" --no-source-selection
```

## AI Relevance Filtering

The tool includes an AI-powered relevance filter that automatically evaluates each paper/article and removes irrelevant results before analysis. This feature:

- **Uses Ollama** to judge relevance based on title and abstract
- **Provides detailed reasons** for each filtering decision (when verbose)
- **Can be disabled** with the `--no-filter` flag
- **Is lenient** with industry news and practical tools
- **Filters aggressively** for papers from unrelated domains (astronomy, biology, etc.)

**Example output:**
```
[2/4] Filtering results for relevance using Ollama (qwen2.5:7b)...
      ✓ KEPT: LinkedIn WhereHows metadata tool (Directly related to metadata management)
      ✗ FILTERED: Reionization Bubbles (Astronomy paper, not related to data platforms)

      Filtering complete: 5/10 results retained
```

To disable filtering and include all search results:
```bash
python -m deep_research.main --topic "your topic" --no-filter
```

## Configuration

You can customize default settings using environment variables in your `.env` file:

```env
# Ollama Configuration (Required)
OLLAMA_BASE_URL=http://172.29.208.1:11434/v1
OLLAMA_API_KEY=ollama-local
OLLAMA_MODEL=llama3.2

# Optional
MAX_RESULTS=10
DEFAULT_DATE_FROM=2024-01-01
OUTPUT_DIR=outputs

# AI Source Selection
ENABLE_SOURCE_SELECTION=true  # Set to "false" to disable and use all sources

# AI Relevance Filtering
ENABLE_RELEVANCE_FILTER=true  # Set to "false" to disable filtering by default
```

## Project Structure

```
deep_research/
├── __init__.py
├── config.py                 # Configuration management
├── models.py                 # Pydantic data models
├── main.py                   # CLI entry point
├── report_generator.py       # Markdown report generation
├── sources/
│   ├── __init__.py
│   ├── arxiv_source.py       # arXiv API integration
│   ├── scholar_source.py     # Semantic Scholar API integration
│   ├── openalex_source.py    # OpenAlex API integration
│   ├── dblp_source.py        # DBLP API integration
│   ├── crossref_source.py    # CrossRef API integration
│   ├── core_source.py        # CORE API integration
│   ├── europepmc_source.py   # Europe PMC API integration
│   ├── web_source.py         # Web and news search integration
│   ├── hackernews_source.py  # HackerNews API integration
│   ├── reddit_source.py      # Reddit search integration
│   ├── github_source.py      # GitHub repository search integration
│   └── google_trends_source.py # Google Trends market analysis
├── synthesis/
│   ├── __init__.py
│   ├── analyzer.py           # Ollama LLM analysis
│   ├── source_selector.py    # AI-powered source selection
│   └── filter.py             # AI relevance filtering
├── outputs/                  # Generated reports (created automatically)
└── tests/                    # Test suite
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=deep_research --cov-report=html
```

### Code Quality

```bash
# Format code
black .

# Run type checking
mypy .

# Run linting
flake8 .
```

## Limitations

This is a **prototype for learning and experimentation**. Current limitations:

- **No caching**: Each search makes fresh API calls
- **Basic error handling**: Limited retry logic and error recovery
- **Markdown only**: No PDF or HTML export yet
- **No database**: Results are not stored for later reference
- **Synchronous**: No async operations (slower for large searches)

## Future Enhancements

Potential improvements for future versions:

- Implement caching to reduce API calls
- Add database storage for research history
- Support PDF and HTML export formats
- Implement async operations for better performance
- Add more sophisticated prompt engineering
- Build a web interface

## Troubleshooting

### "OLLAMA_BASE_URL is required"

Make sure you've created a `.env` file and configured Ollama:
```bash
cp .env.example .env
# Edit .env and add your Ollama settings
```

### Connection errors to Ollama

- Ensure Ollama is running: `ollama serve`
- Check that the base URL in `.env` matches your Ollama instance
- Verify the model is pulled: `ollama list`

### "No results found"

Try:
- Broadening your search topic
- Removing date filters
- Increasing `--max-results`

### Import errors

Make sure you're in the project directory and your virtual environment is activated:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m deep_research.main --topic "your topic"
```

## Contributing

This project follows the monorepo's development standards:

- Black formatting (120 character lines)
- MyPy type checking (strict mode)
- Flake8 linting
- Pre-commit hooks for security scanning

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Ollama](https://ollama.ai) for local LLM inference
- Uses [arXiv API](https://arxiv.org/), [Semantic Scholar](https://www.semanticscholar.org/), [OpenAlex](https://openalex.org/), [DBLP](https://dblp.org/), [CrossRef](https://www.crossref.org/), [CORE](https://core.ac.uk/), and [Europe PMC](https://europepmc.org/) for academic paper search
- Created using Claude Code CLI
