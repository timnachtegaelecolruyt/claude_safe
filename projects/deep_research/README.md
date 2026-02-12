# Deep Research Automation Tool

A Python-based research automation tool that searches academic papers, synthesizes insights using local Ollama models, and generates comprehensive Markdown reports.

## Features

- **Academic Research**: Searches arXiv for relevant papers on any topic
- **AI-Powered Synthesis**: Uses local Ollama models to analyze and extract key insights
- **Markdown Reports**: Generates well-formatted, readable research reports
- **Simple CLI**: Easy-to-use command-line interface
- **Configurable**: Customizable search parameters and date ranges
- **Local & Private**: Runs entirely with local LLM models via Ollama

## What This Tool Does

The Deep Research Tool automates the research process:

1. **Searches** arXiv for academic papers on your topic
2. **Collects** paper metadata, abstracts, and citations
3. **Analyzes** the research using local Ollama models to identify trends and insights
4. **Generates** a comprehensive Markdown report with:
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
- `--max-results` (optional): Maximum number of papers to fetch (default: 10)
- `--date-from` (optional): Start date for filtering papers (YYYY-MM-DD)
- `--date-to` (optional): End date for filtering papers (YYYY-MM-DD)
- `--output` (optional): Custom output filename

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
│   └── arxiv_source.py      # arXiv API integration
├── synthesis/
│   ├── __init__.py
│   └── analyzer.py          # Ollama LLM analysis
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

- **Single data source**: Only searches arXiv (no web scraping, news, or company data yet)
- **No caching**: Each search makes fresh API calls
- **Basic error handling**: Limited retry logic and error recovery
- **Markdown only**: No PDF or HTML export yet
- **No database**: Results are not stored for later reference
- **Synchronous**: No async operations (slower for large searches)

## Future Enhancements

Potential improvements for future versions:

- Add Semantic Scholar integration for citation analysis
- Implement web scraping for market research
- Add company and news data sources
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
- Uses [arXiv API](https://arxiv.org/) for academic paper search
- Created using Claude Code CLI
