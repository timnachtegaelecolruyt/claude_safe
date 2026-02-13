# Quick Start Guide

Get started with the Deep Research Tool in 3 simple steps:

## Step 1: Set up Ollama

Make sure Ollama is running with at least one model available:

```bash
# Check Ollama is accessible
curl http://localhost:11434/api/tags

# If needed, pull a model
ollama pull llama3.2
```

Configure the `.env` file:

```bash
cp .env.example .env
```

The `.env` file should contain:
```
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_API_KEY=ollama-local
OLLAMA_MODEL=llama3.2
```

## Step 2: Run your first research

From the project directory:

```bash
python -m deep_research.main --topic "artificial intelligence" --max-results 5
```

## Step 3: View your report

Reports are saved in `outputs/`:

```bash
cat outputs/research_report_*.md
```

## Example Topics to Try

- "quantum computing error correction"
- "machine learning interpretability"
- "climate change modeling"
- "drug discovery AI"
- "blockchain scalability"
- "renewable energy storage"

## Need Help?

See [README.md](README.md) for full documentation.
