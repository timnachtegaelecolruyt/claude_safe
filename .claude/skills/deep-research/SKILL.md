---
name: deep-research
description: Run deep research automation to search academic papers and generate AI-powered research reports
---

# Deep Research Skill

This skill runs the deep research automation tool to search arXiv for academic papers, analyze them with local Ollama models, and generate comprehensive Markdown research reports.

## Usage

Invoke this skill when the user wants to:
- Research an academic topic
- Get an overview of recent papers in a field
- Generate a research report with AI synthesis
- Analyze academic literature on a subject

## How it works

When invoked, this skill:
1. Searches arXiv for papers on the specified topic
2. Analyzes the papers using local Ollama LLM
3. Generates a comprehensive Markdown report with:
   - Executive summary
   - Key insights and trends
   - Full paper details with citations
4. Saves the report to the outputs directory

## Command Syntax

The skill accepts these arguments:
- Topic (required): The research topic
- `--max-results N`: Maximum papers to analyze (default: 10)
- `--date-from YYYY-MM-DD`: Filter papers from this date
- `--date-to YYYY-MM-DD`: Filter papers until this date
- `--output filename.md`: Custom output filename

## Examples

User might say:
- "Research quantum computing"
- "Do deep research on machine learning with 20 papers"
- "Research climate change from 2024"

## Implementation

```bash
cd /workspaces/claude/claude_safe
poetry run python -m projects.deep_research.main --topic "{{TOPIC}}" {{ARGS}}
```

When the user invokes this skill:

1. Extract the topic from their request
2. Parse any additional arguments (max-results, date filters, output filename)
3. Run the command with appropriate parameters
4. Show the user where the report was saved
5. Optionally display a summary of the results

## Response Format

After running the research:
- Inform the user the research is complete
- Show the path to the generated report
- Display quick summary statistics (papers found, insights generated)
- Offer to read/display the report if requested

## Error Handling

If the command fails:
- Check if Ollama is running
- Verify the .env configuration exists in projects/deep_research/.env
- Ensure dependencies are installed (poetry install)
- Provide helpful troubleshooting steps

## Makefile Integration

This skill can also be invoked via Make:

```bash
make deep-research TOPIC="quantum computing" MAX_RESULTS=10
make deep-research-example  # Quick test with example topic
make deep-research-test     # Run tests
```
