# Contributing to Medical Data

Thank you for your interest in contributing to Medical Data! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Environment Setup](#development-environment-setup)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation Guidelines](#documentation-guidelines)
8. [Submitting Changes](#submitting-changes)
9. [Review Process](#review-process)
10. [Community](#community)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. By participating in this project, you agree to abide by our Code of Conduct:

- **Be respectful**: Treat all contributors with respect and consideration
- **Be collaborative**: Work together and help each other succeed
- **Be inclusive**: Welcome newcomers and people of all backgrounds
- **Be professional**: Keep discussions focused and constructive
- **Be patient**: Remember that everyone is here to learn and improve

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.8 or higher installed
- Git installed and configured
- A GitHub account
- Familiarity with medical data concepts (helpful but not required)

### Finding Ways to Contribute

There are many ways to contribute to Medical Data:

- **Report bugs**: Submit detailed bug reports with reproduction steps
- **Suggest features**: Propose new features or improvements
- **Improve documentation**: Fix typos, clarify instructions, add examples
- **Add datasets**: Contribute information about new medical datasets
- **Write code**: Implement new features or fix bugs
- **Review pull requests**: Help review and test contributions from others

Check our [issue tracker](https://github.com/ai-doctor/medical-data/issues) for:
- Issues labeled `good first issue` - ideal for newcomers
- Issues labeled `help wanted` - we'd appreciate assistance
- Issues labeled `bug` - known bugs that need fixing
- Issues labeled `enhancement` - proposed improvements

## Development Environment Setup

### 1. Fork and Clone the Repository

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/medical-data.git
cd medical-data

# Add upstream remote
git remote add upstream https://github.com/ai-doctor/medical-data.git
```

### 2. Set Up Python Environment with uv

We use [uv](https://github.com/astral-sh/uv) for fast, reliable dependency management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
uv pip install -e ".[dev,docs]"
```

### 3. Install Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
pre-commit install
```

This will automatically run formatters and linters before each commit.

### 4. Verify Installation

```bash
# Run tests to verify setup
make test

# Check code style
make lint

# View all available make commands
make help
```

## Development Workflow

### 1. Create a Feature Branch

Always create a new branch for your changes:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or for bug fixes
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - new features or enhancements
- `fix/` - bug fixes
- `docs/` - documentation changes
- `refactor/` - code refactoring
- `test/` - test additions or modifications

### 2. Make Your Changes

- Write clear, concise code following our [coding standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Commit Your Changes

Write clear commit messages following these guidelines:

```bash
# Good commit message format
git commit -m "Add: New feature for dataset filtering

- Implement filter_by_modality method in MedicalDataBrowser
- Add comprehensive tests for new functionality
- Update documentation with usage examples

Closes #123"
```

Commit message format:
- **First line**: Brief summary (50 chars or less)
- Use imperative mood: "Add" not "Added" or "Adds"
- **Body**: Detailed explanation (wrap at 72 characters)
- Reference relevant issues: `Closes #123`, `Fixes #456`

Commit prefixes:
- `Add:` - new features or files
- `Fix:` - bug fixes
- `Update:` - updates to existing features
- `Refactor:` - code refactoring
- `Docs:` - documentation changes
- `Test:` - test additions or changes
- `Style:` - formatting changes (no code change)
- `Chore:` - maintenance tasks

### 4. Keep Your Branch Updated

Regularly sync with the upstream repository:

```bash
git fetch upstream
git rebase upstream/main
```

### 5. Push Your Changes

```bash
git push origin feature/your-feature-name
```

## Coding Standards

We follow strict coding standards to maintain high code quality:

### Python Code Style (PEP 8)

- **Line length**: Maximum 100 characters
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped and sorted (stdlib, third-party, local)
- **Naming conventions**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private members: `_leading_underscore`

### Type Hints

All functions must include comprehensive type hints:

```python
from typing import List, Optional, Dict, Any

def search_datasets(
    self,
    query: str,
    case_sensitive: bool = False
) -> List[MedicalDataset]:
    """Search for datasets matching a query string."""
    pass
```

### Docstrings

Use Google-style docstrings for all public functions, classes, and modules:

```python
def get_dataset_by_name(self, name: str, exact_match: bool = False) -> Optional[MedicalDataset]:
    """Retrieve a dataset by its name.

    Args:
        name: The dataset name to search for.
        exact_match: If True, requires exact name match (case-insensitive).

    Returns:
        The matching dataset or None if not found.

    Raises:
        ValueError: If the name parameter is empty.

    Example:
        >>> browser = MedicalDataBrowser("README.md")
        >>> browser.parse_readme()
        >>> dataset = browser.get_dataset_by_name("MIMIC-III")
    """
    pass
```

### Code Quality Tools

We use several tools to maintain code quality:

```bash
# Format code with black
make format

# Sort imports with isort
make format

# Lint code with ruff
make lint

# Type check with mypy
make type-check

# Run all quality checks
make check
```

### Error Handling

- Use specific exception types
- Include helpful error messages
- Add logging for important events
- Handle edge cases gracefully

```python
import logging

logger = logging.getLogger(__name__)

def parse_readme(self) -> None:
    """Parse the README markdown file."""
    try:
        with open(self.readme_path, encoding="utf-8") as f:
            content = f.read()
        logger.info("Successfully read README file")
    except IOError as e:
        error_msg = f"Error reading README file: {e}"
        logger.error(error_msg)
        raise IOError(error_msg) from e
```

## Testing Guidelines

### Writing Tests

- All new features must include tests
- Bug fixes should include regression tests
- Aim for high test coverage (>90%)
- Use descriptive test names

Test structure:

```python
import pytest
from medical_data.browser import MedicalDataBrowser

class TestMedicalDataBrowser:
    """Tests for MedicalDataBrowser class."""

    def test_parse_readme_success(self, tmp_path):
        """Test successful parsing of README file."""
        # Arrange
        readme = tmp_path / "README.md"
        readme.write_text("## Medical Imaging Data\n__Dataset Name__\n")
        
        # Act
        browser = MedicalDataBrowser(str(readme))
        browser.parse_readme()
        
        # Assert
        assert len(browser.datasets) > 0

    def test_search_datasets_case_insensitive(self, sample_browser):
        """Test case-insensitive dataset search."""
        results = sample_browser.search_datasets("MRI")
        assert len(results) > 0
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run specific test file
pytest tests/test_browser.py

# Run specific test
pytest tests/test_browser.py::TestMedicalDataBrowser::test_parse_readme_success

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v
```

### Test Organization

- Place tests in the `tests/` directory
- Mirror the source code structure
- Use fixtures for common test data
- Group related tests in classes

### Continuous Integration

All pull requests automatically run:
- Unit tests across Python 3.8, 3.9, 3.10, 3.11, 3.12
- Code style checks (black, isort, ruff)
- Type checking (mypy)
- Coverage analysis

## Documentation Guidelines

### Documentation Types

1. **Code Documentation**:
   - Docstrings for all public APIs
   - Inline comments for complex logic
   - Type hints for all functions

2. **User Documentation**:
   - README.md - project overview and quick start
   - docs/API.md - API reference
   - examples/ - usage examples

3. **Contributor Documentation**:
   - CONTRIBUTING.md (this file)
   - docs/ARCHITECTURE.md - system design
   - docs/CHANGELOG.md - version history

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Keep documentation up-to-date with code changes

### Building Documentation

```bash
# Build Sphinx documentation
make docs

# View documentation locally
make docs-serve

# Check for documentation issues
make docs-check
```

## Submitting Changes

### Pull Request Process

1. **Ensure all checks pass**:
   ```bash
   make check      # Code quality
   make test       # All tests
   make docs       # Documentation builds
   ```

2. **Create a pull request**:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select your feature branch
   - Fill out the PR template completely

3. **Pull Request Checklist**:
   - [ ] Code follows project style guidelines
   - [ ] All tests pass
   - [ ] New tests added for new features
   - [ ] Documentation updated
   - [ ] Commit messages are clear and descriptive
   - [ ] Branch is up-to-date with main
   - [ ] PR description explains changes clearly

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Related Issues
Closes #(issue number)
```

## Review Process

### What to Expect

- **Initial Response**: Within 2-3 business days
- **Review Time**: Usually 3-7 days depending on complexity
- **Feedback**: Constructive comments and suggestions
- **Iterations**: May require changes before approval

### Review Criteria

Reviewers will check for:

1. **Functionality**: Does the code work as intended?
2. **Quality**: Does it follow coding standards?
3. **Tests**: Are there adequate tests?
4. **Documentation**: Is it properly documented?
5. **Design**: Is the implementation well-designed?
6. **Impact**: Are there any unintended side effects?

### Responding to Feedback

- Address all reviewer comments
- Ask questions if something is unclear
- Push additional commits to the same branch
- Mark conversations as resolved when addressed

### After Approval

Once approved and merged:
- Your changes will be included in the next release
- You'll be added to the contributors list
- Delete your feature branch

## Community

### Getting Help

- **GitHub Discussions**: Ask questions and share ideas
- **Issue Tracker**: Report bugs and request features
- **Documentation**: Check our comprehensive docs
- **Email**: contact@medical-data.org for private inquiries

### Recognition

We value all contributions! Contributors are:
- Listed in AUTHORS.md
- Mentioned in release notes
- Credited in commit history
- Part of our community

### Staying Updated

- Watch the repository for notifications
- Follow our release announcements
- Check the changelog for updates
- Join our community discussions

## Additional Resources

### Useful Links

- [Project Homepage](https://github.com/ai-doctor/medical-data)
- [API Documentation](https://github.com/ai-doctor/medical-data/blob/main/docs/API.md)
- [Issue Tracker](https://github.com/ai-doctor/medical-data/issues)
- [Changelog](https://github.com/ai-doctor/medical-data/blob/main/docs/CHANGELOG.md)

### Development Tools

- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- [ruff](https://github.com/astral-sh/ruff) - Fast Python linter
- [black](https://github.com/psf/black) - Python code formatter
- [mypy](https://mypy-lang.org/) - Static type checker
- [pytest](https://pytest.org/) - Testing framework

### Learning Resources

- [PEP 8 Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints Documentation](https://docs.python.org/3/library/typing.html)
- [Git Best Practices](https://git-scm.com/book/en/v2)

## Questions?

If you have questions not covered in this guide:

1. Check existing documentation
2. Search closed issues for similar questions
3. Ask in GitHub Discussions
4. Contact maintainers directly

Thank you for contributing to Medical Data! Together, we're building a valuable resource for the medical machine learning community. 🏥🤖

---

**Last Updated**: 2024
**Version**: 1.0.0
**Maintainers**: Medical Data Contributors