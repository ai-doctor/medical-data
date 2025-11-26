"""Test suite initialization for the medical-data package.

This module initializes the test suite and provides common fixtures, utilities,
and configuration for testing the medical data browser and utilities modules.
It follows pytest best practices with proper setup, fixtures, and helpers for
comprehensive unit and integration testing.

The test suite covers:
- MedicalDataBrowser class functionality
- MedicalDataset dataclass operations
- Utility functions for text processing and filtering
- Dataset validation and export functionality
- Integration tests for complete workflows

Example:
    Run all tests with coverage:
    
    $ pytest tests/ --cov=medical_data --cov-report=term-missing
    
    Run only unit tests:
    
    $ pytest tests/ -m unit
    
    Run with parallel execution:
    
    $ pytest tests/ -n auto

Attributes:
    SAMPLE_README_CONTENT (str): Sample README content for testing.
    SAMPLE_DATASETS (List[MedicalDataset]): Sample datasets for testing.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest

from medical_data.browser import MedicalDataBrowser, MedicalDataset
from medical_data.utils import (
    create_summary_statistics,
    export_datasets_to_json,
    filter_datasets,
    format_dataset_output,
    truncate_text,
    validate_dataset_attributes,
)

# Test configuration constants
SAMPLE_README_CONTENT = """# Medical Machine Learning Datasets

## 1. Medical Imaging Data

__MIMIC-CXR__

A large publicly available database of chest radiographs in DICOM format with free-text radiology reports. The database contains 377,110 images corresponding to 227,835 radiographic studies performed at Beth Israel Deaconess Medical Center between 2011 and 2016.

Paper: https://arxiv.org/abs/1901.07042

Data: https://physionet.org/content/mimic-cxr/2.0.0/

***

__NIH Chest X-ray Dataset__

The NIH Chest X-ray Dataset consists of 112,120 frontal-view X-ray images of 30,805 unique patients with text-mined labels derived from radiological reports. The dataset includes 14 disease labels (e.g., pneumonia, emphysema, pleural effusion).

Paper: https://arxiv.org/abs/1705.02315

Access: https://nihcc.app.box.com/v/ChestXray-NIHCC

***

## 2. Electronic Health Records (EHR) Data

__MIMIC-III__

A large, freely-available database comprising deidentified health-related data from patients who were admitted to the critical care units of the Beth Israel Deaconess Medical Center. The database includes information such as demographics, vital sign measurements, laboratory tests, medications, and more. __Requires registration__.

Paper: https://www.nature.com/articles/sdata201635

Access: https://mimic.mit.edu/

***

## 3. Medical Question/Answer Data

__MedQuAD__

A medical question-answering data set derived from 12 NIH websites. It contains 47,457 medical question-answer pairs.

Paper: https://arxiv.org/abs/1901.08079

Data: https://github.com/abachaa/MedQuAD

***
"""


@pytest.fixture(scope="session")
def sample_readme_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a temporary README file with sample medical dataset content.
    
    This fixture creates a temporary markdown file containing sample medical
    dataset information that can be used for testing the MedicalDataBrowser
    parsing and search functionality.
    
    Args:
        tmp_path_factory: Pytest fixture for creating temporary directories.
        
    Returns:
        Path object pointing to the temporary README file.
        
    Example:
        >>> def test_browser_parsing(sample_readme_file):
        ...     browser = MedicalDataBrowser(str(sample_readme_file))
        ...     browser.parse_readme()
        ...     assert len(browser.datasets) > 0
    """
    readme_path = tmp_path_factory.mktemp("data") / "README.md"
    readme_path.write_text(SAMPLE_README_CONTENT, encoding="utf-8")
    return readme_path


@pytest.fixture(scope="session")
def sample_datasets() -> List[MedicalDataset]:
    """Provide a list of sample MedicalDataset objects for testing.
    
    Creates a diverse set of medical datasets with various attributes for
    comprehensive testing of filtering, searching, and analysis functions.
    
    Returns:
        List of MedicalDataset objects with varied attributes.
        
    Example:
        >>> def test_filtering(sample_datasets):
        ...     imaging = [d for d in sample_datasets if d.category == "Medical Imaging Data"]
        ...     assert len(imaging) > 0
    """
    return [
        MedicalDataset(
            name="MIMIC-CXR",
            category="Medical Imaging Data",
            description="A large publicly available database of chest radiographs.",
            paper_url="https://arxiv.org/abs/1901.07042",
            data_url="https://physionet.org/content/mimic-cxr/2.0.0/",
            requires_registration=False,
        ),
        MedicalDataset(
            name="NIH Chest X-ray Dataset",
            category="Medical Imaging Data",
            description="112,120 frontal-view X-ray images with 14 disease labels.",
            paper_url="https://arxiv.org/abs/1705.02315",
            access_url="https://nihcc.app.box.com/v/ChestXray-NIHCC",
            requires_registration=False,
        ),
        MedicalDataset(
            name="MIMIC-III",
            category="Electronic Health Records (EHR) Data",
            description="Deidentified health-related data from critical care units.",
            paper_url="https://www.nature.com/articles/sdata201635",
            access_url="https://mimic.mit.edu/",
            requires_registration=True,
        ),
        MedicalDataset(
            name="MedQuAD",
            category="Medical Question/Answer Data",
            description="47,457 medical question-answer pairs from NIH websites.",
            paper_url="https://arxiv.org/abs/1901.08079",
            data_url="https://github.com/abachaa/MedQuAD",
            requires_registration=False,
        ),
    ]


@pytest.fixture(scope="function")
def browser_instance(sample_readme_file: Path) -> MedicalDataBrowser:
    """Create a MedicalDataBrowser instance with parsed sample data.
    
    This fixture provides a fully initialized and parsed browser instance
    ready for testing search, filtering, and analysis functionality.
    
    Args:
        sample_readme_file: Path to temporary README file (from fixture).
        
    Returns:
        Initialized and parsed MedicalDataBrowser instance.
        
    Example:
        >>> def test_search(browser_instance):
        ...     results = browser_instance.search_datasets("chest")
        ...     assert len(results) > 0
    """
    browser = MedicalDataBrowser(str(sample_readme_file))
    browser.parse_readme()
    return browser


@pytest.fixture(scope="function")
def temp_json_file(tmp_path: Path) -> Path:
    """Create a temporary JSON file path for export testing.
    
    Args:
        tmp_path: Pytest fixture for temporary directory.
        
    Returns:
        Path object for a temporary JSON file.
        
    Example:
        >>> def test_export(sample_datasets, temp_json_file):
        ...     export_datasets_to_json(sample_datasets, temp_json_file)
        ...     assert temp_json_file.exists()
    """
    return tmp_path / "test_export.json"


@pytest.fixture(scope="function")
def empty_dataset() -> MedicalDataset:
    """Create a minimal MedicalDataset with only required fields.
    
    Useful for testing validation and edge cases.
    
    Returns:
        MedicalDataset with minimal attributes.
        
    Example:
        >>> def test_validation(empty_dataset):
        ...     is_valid, missing = validate_dataset_attributes(empty_dataset)
        ...     assert is_valid
    """
    return MedicalDataset(name="Test Dataset", category="Test Category")


@pytest.fixture(scope="function")
def full_dataset() -> MedicalDataset:
    """Create a MedicalDataset with all optional fields populated.
    
    Useful for testing formatting and complete functionality.
    
    Returns:
        MedicalDataset with all attributes populated.
        
    Example:
        >>> def test_full_formatting(full_dataset):
        ...     output = format_dataset_output(full_dataset, detailed=True)
        ...     assert "Paper:" in output
    """
    return MedicalDataset(
        name="Complete Test Dataset",
        category="Test Category",
        description="A comprehensive test dataset with all fields populated.",
        paper_url="https://example.com/paper",
        access_url="https://example.com/access",
        data_url="https://example.com/data",
        information_url="https://example.com/info",
        overview_url="https://example.com/overview",
        requires_registration=True,
        raw_text="Complete raw text content for testing",
    )


# Helper functions for tests


def assert_dataset_valid(dataset: MedicalDataset) -> None:
    """Assert that a dataset has valid required attributes.
    
    Args:
        dataset: MedicalDataset object to validate.
        
    Raises:
        AssertionError: If dataset is missing required attributes.
        
    Example:
        >>> def test_dataset_creation(sample_datasets):
        ...     for dataset in sample_datasets:
        ...         assert_dataset_valid(dataset)
    """
    assert hasattr(dataset, "name"), "Dataset must have a name"
    assert hasattr(dataset, "category"), "Dataset must have a category"
    assert isinstance(dataset.name, str), "Dataset name must be a string"
    assert isinstance(dataset.category, str), "Dataset category must be a string"
    assert len(dataset.name) > 0, "Dataset name cannot be empty"
    assert len(dataset.category) > 0, "Dataset category cannot be empty"


def assert_url_valid(url: str) -> None:
    """Assert that a URL string is valid.
    
    Args:
        url: URL string to validate.
        
    Raises:
        AssertionError: If URL format is invalid.
        
    Example:
        >>> def test_urls(sample_datasets):
        ...     for dataset in sample_datasets:
        ...         if dataset.paper_url:
        ...             assert_url_valid(dataset.paper_url)
    """
    assert isinstance(url, str), "URL must be a string"
    assert url.startswith(("http://", "https://")), "URL must start with http:// or https://"
    assert len(url) > 10, "URL seems too short to be valid"


def create_test_readme(content: str, path: Path) -> None:
    """Create a test README file with specified content.
    
    Args:
        content: Markdown content to write to the file.
        path: Path where the README should be created.
        
    Example:
        >>> def test_custom_content(tmp_path):
        ...     readme_path = tmp_path / "README.md"
        ...     create_test_readme("# Test", readme_path)
        ...     assert readme_path.exists()
    """
    path.write_text(content, encoding="utf-8")


def load_json_datasets(json_path: Path) -> List[Dict[str, Any]]:
    """Load datasets from a JSON export file.
    
    Args:
        json_path: Path to the JSON file.
        
    Returns:
        List of dataset dictionaries loaded from JSON.
        
    Example:
        >>> def test_json_roundtrip(sample_datasets, temp_json_file):
        ...     export_datasets_to_json(sample_datasets, temp_json_file)
        ...     loaded = load_json_datasets(temp_json_file)
        ...     assert len(loaded) == len(sample_datasets)
    """
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


# Test markers and categories
pytest_plugins = []

# Version information
__version__ = "1.0.0"
__all__ = [
    "sample_readme_file",
    "sample_datasets",
    "browser_instance",
    "temp_json_file",
    "empty_dataset",
    "full_dataset",
    "assert_dataset_valid",
    "assert_url_valid",
    "create_test_readme",
    "load_json_datasets",
    "SAMPLE_README_CONTENT",
]