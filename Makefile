.PHONY: help install setup test lint format clean pre-commit-install pre-commit-run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

setup: install pre-commit-install ## Complete setup (install dependencies + pre-commit hooks)
	@echo "✅ Setup complete! You're ready to start developing."

pre-commit-install: ## Install pre-commit hooks
	poetry run pre-commit install
	@echo "✅ Pre-commit hooks installed"

pre-commit-run: ## Run pre-commit hooks on all files
	poetry run pre-commit run --all-files

test: ## Run tests with pytest
	poetry run pytest

lint: ## Run linting checks
	poetry run flake8 projects/
	poetry run mypy projects/

format: ## Format code with black
	poetry run black projects/

format-check: ## Check code formatting without making changes
	poetry run black --check projects/

security-scan: ## Run security scans
	poetry run pre-commit run gitleaks --all-files
	poetry run pre-commit run detect-secrets --all-files

clean: ## Clean up cache and temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	@echo "✅ Cleaned up cache and temporary files"

validate: lint test ## Run validation checks (lint + test)
	@echo "✅ All validation checks passed"

# Deep Research project commands
deep-research: ## Run deep research tool (usage: make deep-research TOPIC="your topic" MAX_RESULTS=10)
	@if [ -z "$(TOPIC)" ]; then \
		echo "Error: TOPIC is required. Usage: make deep-research TOPIC=\"quantum computing\""; \
		exit 1; \
	fi
	poetry run python -m projects.deep_research.main --topic "$(TOPIC)" $(if $(MAX_RESULTS),--max-results $(MAX_RESULTS),) $(if $(DATE_FROM),--date-from $(DATE_FROM),) $(if $(DATE_TO),--date-to $(DATE_TO),) $(if $(OUTPUT),--output $(OUTPUT),)

deep-research-test: ## Run deep research tests
	poetry run pytest projects/deep_research/

deep-research-example: ## Run deep research with example topic
	poetry run python -m projects.deep_research.main --topic "quantum computing" --max-results 5
