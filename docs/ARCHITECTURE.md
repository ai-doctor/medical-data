Main readme file:

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

## Development

Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

Run tests:
```bash
make test
```

Format code:
```bash
make format
```

Lint code:
```bash
make lint
```

Type check:
```bash
make type-check
```

## Project Structure

```
medical-data/
├── src/
│   └── medical_data/
│       ├── __init__.py
│       ├── cli.py
│       ├── parsers/
│       │   ├── __init__.py
│       │   ├── dicom_parser.py
│       │   ├── hl7_parser.py
│       │   └── fhir_parser.py
│       ├── validators/
│       │   ├── __init__.py
│       │   └── data_validator.py
│       └── utils/
│           ├── __init__.py
│           └── logger.py
├── tests/
├── docs/
├── pyproject.toml
├── Makefile
└── README.md
```

## License

MIT License

Key source files:
- src/medical_data/__init__.py
- src/medical_data/cli.py
- src/medical_data/parsers/__init__.py
- src/medical_data/parsers/dicom_parser.py
- src/medical_data/parsers/hl7_parser.py
- src/medical_data/parsers/fhir_parser.py
- src/medical_data/validators/__init__.py
- src/medical_data/validators/data_validator.py
- src/medical_data/utils/__init__.py
- src/medical_data/utils/logger.py