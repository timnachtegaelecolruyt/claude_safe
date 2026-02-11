# claude_safe

A secure monorepo for Claude Code projects with automated security checks
and quality controls.

## Security Features

This repository implements multiple layers of security to prevent accidental
publication of sensitive data:

### Pre-commit Hooks

Automatically run before every commit to catch issues early:

- **Secret Detection**: Scans for API keys, passwords, and credentials
  using `detect-secrets` and `gitleaks`
- **File Size Limits**: Prevents committing files larger than 1MB
- **Private Key Detection**: Blocks commits containing private keys
- **Branch Protection**: Prevents direct commits to main/master branches
- **Code Quality**: Runs linters and formatters
  (Python, JavaScript, Markdown, Shell)

### Continuous Integration (CI)

GitHub Actions workflows that run on every push and pull request:

- **Secret Scanning**: Full repository scan with Gitleaks
- **CodeQL Analysis**: Advanced security vulnerability detection
- **Dependency Review**: Checks for vulnerable dependencies in PRs
- **File Size Validation**: Ensures no large files slip through
- **Structure Validation**: Verifies repository integrity

## 🚀 Quick Start

### First-Time Setup

1. **Install pre-commit**:

   ```bash
   pip install pre-commit
   ```

2. **Install the git hooks**:

   ```bash
   cd claude_safe
   pre-commit install
   ```

3. **Test the hooks** (optional):

   ```bash
   pre-commit run --all-files
   ```

### Working with the Repository

1. **Create a new branch** (never commit directly to main):

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit:

   ```bash
   git add .
   git commit -m "Your commit message"
   ```

   The pre-commit hooks will run automatically. If they fail, fix the
   issues and commit again.

3. **Push your branch**:

   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub
   - CI checks will run automatically
   - All checks must pass before merging

## 📁 Monorepo Structure

```text
claude_safe/
├── .github/
│   └── workflows/          # CI/CD pipelines
├── .pre-commit-config.yaml # Pre-commit hook configuration
├── .secrets.baseline       # Known safe "secrets" (false positives)
├── projects/               # Individual projects go here
│   ├── project1/
│   ├── project2/
│   └── ...
└── README.md
```

## 🛡️ Security Best Practices

1. **Never commit secrets**: Use environment variables or secret management tools
2. **Keep files small**: Large files bloat the repository and slow down operations
3. **Review before pushing**: Always review your changes before pushing
4. **Use branches**: Create feature branches and use pull requests for code review
5. **Update dependencies**: Regularly update dependencies to patch security vulnerabilities
6. **Scan locally**: Run `pre-commit run --all-files` before pushing to catch issues early

## 🔧 Configuration

### Adding False Positives to Secret Detection

If detect-secrets flags a false positive:

1. Add it to the baseline:

   ```bash
   detect-secrets scan --baseline .secrets.baseline
   ```

2. Commit the updated baseline:

   ```bash
   git add .secrets.baseline
   git commit -m "Update secrets baseline"
   ```

### Customizing Pre-commit Hooks

Edit [.pre-commit-config.yaml](.pre-commit-config.yaml) to:

- Add/remove hooks
- Adjust file size limits
- Configure linter rules
- Exclude specific files or patterns

### Updating Hooks

```bash
pre-commit autoupdate
```

## 🚨 Bypassing Hooks (Emergency Only)

In rare cases where you need to bypass pre-commit hooks:

```bash
git commit --no-verify -m "Emergency fix"
```

**⚠️ WARNING**: This skips all security checks. Only use in emergencies
and ensure manual review.

## 📊 CI Status

All CI checks must pass before merging:

- ✅ Pre-commit hooks
- ✅ Secret scanning (Gitleaks)
- ✅ File size validation
- ✅ CodeQL security analysis
- ✅ Dependency review (PRs only)
- ✅ Repository structure validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all pre-commit hooks pass
5. Push to your fork
6. Create a Pull Request

## 📝 License

This is a private repository for Claude Code projects.

## 🔗 Resources

- [Pre-commit documentation](https://pre-commit.com/)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [detect-secrets](https://github.com/Yelp/detect-secrets)
- [GitHub Actions](https://docs.github.com/en/actions)
- [CodeQL](https://codeql.github.com/)
