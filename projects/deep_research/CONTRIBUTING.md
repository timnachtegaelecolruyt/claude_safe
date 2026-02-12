# Contributing to Deep Research

Thank you for your interest in contributing to Deep Research! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/deep-research.git
   cd deep-research
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up Ollama**:
   - Install Ollama from https://ollama.ai
   - Pull a model: `ollama pull llama3.2`
   - Configure `.env` with your settings

## Code Standards

This project follows these coding standards:

- **Formatting**: Black with 120 character line length
- **Type Checking**: MyPy in strict mode
- **Linting**: Flake8
- **Testing**: pytest with coverage

### Running Quality Checks

```bash
# Format code
black .

# Type checking
mypy .

# Linting
flake8 .

# Tests with coverage
pytest --cov=deep_research --cov-report=html
```

## Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code standards

3. **Add tests** for new functionality

4. **Run the test suite**:
   ```bash
   pytest
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Ensure all tests pass
- Add tests for new features
- Update documentation as needed
- Follow the existing code style

## Code Review Process

- All submissions require review
- Reviewers may suggest changes
- Once approved, a maintainer will merge the PR

## Reporting Issues

When reporting issues, please include:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, Ollama version)
- Relevant logs or error messages

## Feature Requests

Feature requests are welcome! Please:

- Check if the feature already exists
- Provide a clear use case
- Describe the proposed solution
- Consider implementation complexity

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect differing viewpoints

## Questions?

Feel free to open an issue for questions or discussion.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
