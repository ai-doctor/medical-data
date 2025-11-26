# Medical Data Analysis System

A production-ready medical data analysis system with support for various medical data formats including DICOM, HL7, and FHIR.

## Installation

Using uv (recommended):
```bash
uv pip install -e .
```

Traditional pip:
```bash
pip install -e .
```

## Features

- Support for multiple medical data formats (DICOM, HL7, FHIR)
- Comprehensive data validation and parsing
- Command-line interface for easy data processing
- Extensive documentation and examples

## Development

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/ai-doctor/medical-data.git
cd medical-data
```

2. Install development dependencies using uv:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev,docs]"
```

3. Install pre-commit hooks:
```bash
pre-commit install
```

### Running Tests and Checks

```bash
# Run tests
make test

# Run tests with coverage
make test-coverage

# Lint code
make lint

# Format code
make format

# Type check
make type-check

# Run all checks
make check
```

## Documentation

- [API Documentation](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Contribution Guidelines](docs/CONTRIBUTING.md)

## Examples

See the [examples](examples/) directory for usage examples, including:
- Basic usage examples
- Advanced filtering examples
- Batch export examples

## Contributing

We welcome contributions! Please see our [Contribution Guidelines](docs/CONTRIBUTING.md) for details on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Community

- [GitHub Discussions](https://github.com/ai-doctor/medical-data/discussions)
- [Issue Tracker](https://github.com/ai-doctor/medical-data/issues)

## Acknowledgments

- List of contributors and acknowledgments

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the latest changes and version history.