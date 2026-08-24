# Contributing

## Welcome to EZ

Thank you for your interest in contributing to EZ (Signature Preservation and Isolation Engine)!

## How to Contribute

### 1. Fork and Clone

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/ez-signature-extraction.git
cd ez-signature-extraction
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Follow the [Development Guidelines](DEVELOPMENT_GUIDELINES.md)
- Add tests for new functionality
- Update documentation as needed

### 4. Run Tests

```bash
python -m unittest discover -s backend/tests
```

All 103 tests must pass.

### 5. Commit and Push

```bash
git add .
git commit -m "feat: Add your feature description"
git push origin feature/your-feature-name
```

### 6. Create Pull Request

Submit a PR on the main repository with a clear description of changes.

---

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip or uv package manager

### Installation

```bash
# Clone and enter directory
git clone https://github.com/nousresearch/ez-signature-extraction.git
cd ez-signature-extraction

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
python -m unittest discover -s backend/tests

# Run specific test file
python -m unittest backend.tests.test_signature_refiner

# Run with verbose output
python -m unittest -v backend.tests.test_signature_refiner
```

---

## Pull Request Process

### Before Submitting

1. **Run all tests** - Ensure 103 tests pass
2. **Update documentation** - Any new features need docs
3. **Add tests** - Cover new code paths
4. **Check type hints** - All functions should have them
5. **Follow style** - PEP 8, docstrings, etc.

### PR Description

Include in your PR:

```
## What does this PR do?

Brief description of changes.

## How was it tested?

- Test 1: Description
- Test 2: Description

## Any breaking changes?

No / Yes (describe)

## Related issues

Fixes #123
```

---

## Code Review Guidelines

Reviewers will check:

- [ ] Tests pass
- [ ] Type hints present
- [ ] Documentation updated
- [ ] Follows coding standards
- [ ] No performance regressions
- [ ] Proper error handling

---

## Development Environment

### Recommended Tools

- **IDE:** VS Code with Python extension
- **Linter:** flake8 (via pre-commit)
- **Type Checker:** mypy
- **Formatter:** black

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

---

## Project Philosophy

Please read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) and [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) to understand EZ's core principles:

- **Signature preservation > everything else**
- **No AI/ML in Version 1**
- **Traditional computer vision only**
- **Blue ink signatures only**
- **Immutability principle**

---

## Questions?

- Open an issue for questions
- Check existing issues before creating new ones
- Be patient - maintainers are volunteers

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.