# Contributing to ConfigSmith

Thank you for your interest in contributing to ConfigSmith! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git

### Development Setup

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/YOUR_USERNAME/ConfigSmith.git
   cd ConfigSmith
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to verify setup**

   ```bash
   pytest tests/ -v
   ```

## 📝 Development Workflow

### Code Style

We follow PEP 8 with these tools:

- **Black** for formatting
- **Ruff** for linting
- **MyPy** for type checking

Run before committing:

```bash
black src/ tests/
ruff check src/ tests/
mypy src/
```

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

Examples:

```
feat: add support for Deno.env patterns
fix: handle quoted values in .env parsing
docs: add troubleshooting section to README
test: add edge case tests for TypeScript scanner
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation

## 🧪 Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_python_scanner.py -v

# With coverage
pytest tests/ --cov=configsmith --cov-report=html
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_detects_environ_subscript`
- Include docstrings explaining what's being tested
- Add fixtures to `tests/fixtures/` for test data

## 📁 Project Structure

```
ConfigSmith/
├── src/configsmith/
│   ├── __init__.py      # Package exports
│   ├── cli.py           # CLI commands
│   ├── models.py        # Data models
│   ├── parser.py        # .env file parser
│   ├── merge.py         # Merge logic
│   ├── generator.py     # Output generator
│   └── scanners/
│       ├── python_scanner.py
│       └── typescript_scanner.py
├── tests/
│   ├── fixtures/        # Test data files
│   ├── test_*.py        # Test modules
└── pyproject.toml       # Project config
```

## 🐛 Reporting Issues

When reporting bugs, please include:

1. Python version (`python --version`)
2. ConfigSmith version (`configsmith --version`)
3. Operating system
4. Minimal reproduction steps
5. Expected vs actual behavior

## 💡 Feature Requests

For new features:

1. Check existing issues first
2. Describe the use case
3. Provide examples if possible

## 📋 Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.
