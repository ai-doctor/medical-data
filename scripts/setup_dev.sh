# Repository Summary

**Project Name:** ai-doctor/medical-data
**Total Files:** 22

## Directory Structure

```
ai-doctor/medical-data/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── API.md
│   ├── CONTRIBUTING.md
│   ├── USER_GUIDE.md
│   └── architecture.md
├── scripts/
│   └── .gitkeep
├── src/
│   └── medical_data/
│       ├── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes.py
│       │   └── schemas.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── db/
│       │   ├── __init__.py
│       │   ├── connection.py
│       │   └── models.py
│       └── utils/
│           ├── __init__.py
│           ├── logger.py
│           └── validators.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_db.py
│   └── test_validators.py
├── .gitignore
├── LICENSE
├── Makefile
├── README.md
└── pyproject.toml
```

## Key Files

### README.md (7.0 KB)
- Comprehensive documentation for the Medical Data Management System
- Includes installation instructions, features, usage examples, and API documentation
- Well-structured with clear sections and code examples

### pyproject.toml (3.2 KB)
- Modern Python project configuration using PEP 621
- Configured for uv package manager
- Includes all dependencies (FastAPI, SQLAlchemy, PostgreSQL, etc.)
- Defines development dependencies and tools (pytest, ruff, mypy, black)
- Project metadata and entry points defined

### Makefile (1.9 KB)
- Comprehensive build automation
- Targets for installation, testing, linting, formatting, and cleanup
- Uses uv for dependency management
- Includes quality checks and development server commands

### src/medical_data/config/settings.py (2.0 KB)
- Pydantic-based configuration management
- Environment variable support
- Database, API, and logging settings
- Security configurations

### tests/ (Various test files)
- Comprehensive test suite using pytest
- Tests for API, database, and validators
- Includes conftest.py for test fixtures

### docs/ (Multiple documentation files)
- API.md: API documentation with endpoints
- USER_GUIDE.md: User guide for the system
- CONTRIBUTING.md: Contribution guidelines
- architecture.md: System architecture documentation

## Technology Stack

- **Python**: Modern async framework
- **FastAPI**: Web framework for API
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Database (via asyncpg)
- **Pydantic**: Data validation
- **uv**: Package manager (astral-sh)
- **pytest**: Testing framework
- **ruff/black**: Code quality tools

## Project Status

This appears to be a medical data management system with:
- RESTful API for managing patient records, appointments, and medical records
- Async database operations with PostgreSQL
- Modern Python tooling and best practices
- Comprehensive testing and documentation
- CI/CD with GitHub Actions