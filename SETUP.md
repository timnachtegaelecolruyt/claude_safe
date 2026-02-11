# Setup Guide

This guide will help you set up the development environment for the claude_safe monorepo.

## Prerequisites

- Python 3.10 or higher
- Git
- Poetry (Python package manager)

## Installing Poetry

### Option 1: Official Installer (Recommended)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Add Poetry to your PATH (add to your `~/.bashrc` or `~/.zshrc`):
```bash
export PATH="$HOME/.local/bin:$PATH"
```

Reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Option 2: pip (Alternative)
```bash
pip install --user poetry
```

### Verify Installation
```bash
poetry --version
```

## Project Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone git@github.com:timnachtegaelecolruyt/claude_safe.git
   cd claude_safe
   ```

2. **Run the setup command**:
   ```bash
   make setup
   ```

   This will:
   - Install all Python dependencies
   - Install pre-commit hooks
   - Configure the development environment

3. **Verify the setup**:
   ```bash
   make pre-commit-run
   ```

   This runs all pre-commit hooks to ensure everything is working correctly.

## Available Commands

Use `make help` to see all available commands:

```bash
make help
```

### Common Commands

- `make install` - Install dependencies
- `make setup` - Complete initial setup
- `make test` - Run tests
- `make lint` - Run linting checks
- `make format` - Format code with black
- `make security-scan` - Run security scans
- `make clean` - Clean up cache files

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** in the `projects/` directory

3. **Run validation checks**:
   ```bash
   make validate
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Your commit message"
   ```

   Pre-commit hooks will run automatically and prevent commits if:
   - Code has syntax errors
   - Secrets are detected
   - Files are too large
   - Code doesn't meet style guidelines

5. **Push to GitHub**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Troubleshooting

### Pre-commit hooks failing

If pre-commit hooks fail:
1. Read the error message carefully
2. Fix the issues identified
3. Try committing again

### Poetry not found

Ensure Poetry is in your PATH:
```bash
echo $PATH
```

If not, add it to your shell configuration file.

### Network issues

If you're behind a corporate proxy:
```bash
poetry config http-basic.pypi <username> <password>
```

### Python version issues

Check your Python version:
```bash
python3 --version
```

Ensure it's 3.10 or higher.

## IDE Setup

### VSCode

Recommended extensions:
- Python
- Pylance
- Black Formatter
- GitLens

Settings (`.vscode/settings.json`):
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true
}
```

### PyCharm

1. Set Poetry as the project interpreter
2. Enable "Black" as the formatter
3. Enable "Flake8" as the linter

## Next Steps

- Read the [README.md](README.md) for project documentation
- Check the [claude.md](claude.md) for working guidelines
- Start building your first project in the `projects/` directory
