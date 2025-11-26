"""Utility functions for the medical data browser package.

This module provides comprehensive utility functions for working with medical datasets,
including text processing, data filtering, formatting, validation, and statistical analysis.
All functions follow PEP 8 standards with complete type hints, docstrings, error handling,
and input validation for production use.

The module is designed to support the medical data browser and can be used independently
for medical dataset analysis tasks.

Example:
    Basic usage of utility functions:

    >>> from medical_data.utils import truncate_text, format_dataset_output
    >>> text = "This is a very long description of a medical dataset..."
    >>> short_text = truncate_text(text, max_length=50)
    >>> print(short_text)
    'This is a very long description of a medical...'

Attributes:
    logger (logging.Logger): Module-level logger for utility operations.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

# Configure module logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = "...",
    respect_word_boundaries: bool = True,
) -> str:
    """Truncate text to a maximum length with optional suffix.

    This function intelligently truncates text while optionally respecting
    word boundaries to avoid cutting words in the middle.

    Args:
        text: The text to truncate.
        max_length: Maximum length of the truncated text (including suffix).
        suffix: String to append when text is truncated.
        respect_word_boundaries: If True, avoid cutting words in the middle.

    Returns:
        The truncated text with suffix if applicable.

    Raises:
        ValueError: If max_length is less than the length of suffix.
        TypeError: If text is not a string.

    Example:
        >>> truncate_text("This is a long text", max_length=15)
        'This is a...'
        >>> truncate_text("Short", max_length=15)
        'Short'
    """
    if not isinstance(text, str):
        raise TypeError(f"Text must be a string, got {type(text)}")

    if max_length < len(suffix):
        raise ValueError(
            f"max_length ({max_length}) must be >= suffix length ({len(suffix)})"
        )

    # Clean whitespace
    text = " ".join(text.split())

    # Return as-is if already short enough
    if len(text) <= max_length:
        return text

    # Calculate truncation point
    truncate_at = max_length - len(suffix)

    if respect_word_boundaries and truncate_at > 0:
        # Find the last space before truncation point
        last_space = text.rfind(" ", 0, truncate_at)
        if last_space > 0:
            truncate_at = last_space

    return text[:truncate_at].rstrip() + suffix


def format_dataset_output(
    dataset: Any,
    detailed: bool = False,
    include_urls: bool = True,
    indent: int = 2,
) -> str:
    """Format a dataset object for display output.

    Creates a human-readable string representation of a medical dataset
    with configurable detail level and formatting.

    Args:
        dataset: The MedicalDataset object to format.
        detailed: If True, include full description and all metadata.
        include_urls: If True, include access URLs in the output.
        indent: Number of spaces for indentation.

    Returns:
        Formatted string representation of the dataset.

    Raises:
        AttributeError: If dataset doesn't have required attributes.

    Example:
        >>> from medical_data.browser import MedicalDataset
        >>> dataset = MedicalDataset(name="Test", category="Imaging")
        >>> print(format_dataset_output(dataset))
        Name: Test
        Category: Imaging
    """
    indent_str = " " * indent
    lines: List[str] = []

    # Basic information (always included)
    lines.append(f"Name: {dataset.name}")
    lines.append(f"Category: {dataset.category}")

    # Description
    if hasattr(dataset, "description") and dataset.description:
        if detailed:
            lines.append(f"Description: {dataset.description}")
        else:
            short_desc = truncate_text(dataset.description, max_length=100)
            lines.append(f"Description: {short_desc}")

    # URLs
    if include_urls:
        url_fields = [
            ("Paper", "paper_url"),
            ("Access", "access_url"),
            ("Data", "data_url"),
            ("Information", "information_url"),
            ("Overview", "overview_url"),
        ]

        for label, attr in url_fields:
            if hasattr(dataset, attr) and getattr(dataset, attr):
                lines.append(f"{label}: {getattr(dataset, attr)}")

    # Registration requirement
    if hasattr(dataset, "requires_registration") and dataset.requires_registration:
        lines.append("⚠️  Registration Required")

    # Add indentation
    return "\n".join(indent_str + line for line in lines)


def filter_datasets(
    datasets: List[Any],
    criteria: Dict[str, Any],
    match_all: bool = True,
) -> List[Any]:
    """Filter datasets based on multiple criteria.

    Provides flexible filtering of datasets based on attribute values.
    Can require all criteria to match (AND logic) or any criteria (OR logic).

    Args:
        datasets: List of MedicalDataset objects to filter.
        criteria: Dictionary mapping attribute names to required values.
            Values can be exact matches or callable predicates.
        match_all: If True, all criteria must match (AND). If False,
            any criterion can match (OR).

    Returns:
        List of datasets matching the filter criteria.

    Raises:
        TypeError: If datasets is not a list or criteria is not a dict.

    Example:
        >>> from medical_data.browser import MedicalDataset
        >>> datasets = [MedicalDataset(name="A", category="Imaging")]
        >>> filtered = filter_datasets(
        ...     datasets,
        ...     {"category": "Imaging", "requires_registration": False}
        ... )
    """
    if not isinstance(datasets, list):
        raise TypeError(f"datasets must be a list, got {type(datasets)}")

    if not isinstance(criteria, dict):
        raise TypeError(f"criteria must be a dict, got {type(criteria)}")

    if not criteria:
        return datasets

    filtered: List[Any] = []

    for dataset in datasets:
        matches = []

        for attr_name, expected_value in criteria.items():
            if not hasattr(dataset, attr_name):
                matches.append(False)
                continue

            actual_value = getattr(dataset, attr_name)

            # If expected_value is callable, use it as a predicate
            if callable(expected_value):
                matches.append(expected_value(actual_value))
            else:
                # Direct comparison
                if isinstance(expected_value, str) and isinstance(actual_value, str):
                    # Case-insensitive string comparison
                    matches.append(expected_value.lower() in actual_value.lower())
                else:
                    matches.append(actual_value == expected_value)

        # Apply AND/OR logic
        if match_all and all(matches):
            filtered.append(dataset)
        elif not match_all and any(matches):
            filtered.append(dataset)

    logger.info(
        "Filtered %d datasets from %d using %d criteria",
        len(filtered),
        len(datasets),
        len(criteria),
    )

    return filtered


def create_summary_statistics(datasets: List[Any]) -> Dict[str, Any]:
    """Create comprehensive summary statistics for a list of datasets.

    Analyzes a collection of medical datasets and produces detailed statistics
    including counts, category breakdowns, access information, and more.

    Args:
        datasets: List of MedicalDataset objects to analyze.

    Returns:
        Dictionary containing various statistical measures and breakdowns.

    Raises:
        TypeError: If datasets is not a list.
        ValueError: If datasets list is empty.

    Example:
        >>> from medical_data.browser import MedicalDataset
        >>> datasets = [MedicalDataset(name="Test", category="Imaging")]
        >>> stats = create_summary_statistics(datasets)
        >>> print(stats["total_datasets"])
        1
    """
    if not isinstance(datasets, list):
        raise TypeError(f"datasets must be a list, got {type(datasets)}")

    if not datasets:
        raise ValueError("Cannot create statistics for empty dataset list")

    stats: Dict[str, Any] = {
        "total_datasets": len(datasets),
        "categories": set(),
        "category_counts": {},
        "datasets_with_papers": 0,
        "datasets_with_access": 0,
        "datasets_requiring_registration": 0,
        "url_statistics": {
            "paper_urls": 0,
            "access_urls": 0,
            "data_urls": 0,
            "information_urls": 0,
            "overview_urls": 0,
        },
        "description_statistics": {
            "with_description": 0,
            "average_description_length": 0,
            "max_description_length": 0,
            "min_description_length": float("inf"),
        },
    }

    description_lengths: List[int] = []

    for dataset in datasets:
        # Category tracking
        if hasattr(dataset, "category"):
            category = dataset.category
            stats["categories"].add(category)
            stats["category_counts"][category] = (
                stats["category_counts"].get(category, 0) + 1
            )

        # URL tracking
        if hasattr(dataset, "paper_url") and dataset.paper_url:
            stats["datasets_with_papers"] += 1
            stats["url_statistics"]["paper_urls"] += 1

        url_attrs = ["access_url", "data_url", "information_url", "overview_url"]
        has_access = False
        for attr in url_attrs:
            if hasattr(dataset, attr) and getattr(dataset, attr):
                has_access = True
                stats["url_statistics"][f"{attr}s"] += 1

        if has_access:
            stats["datasets_with_access"] += 1

        # Registration requirement
        if hasattr(dataset, "requires_registration") and dataset.requires_registration:
            stats["datasets_requiring_registration"] += 1

        # Description statistics
        if hasattr(dataset, "description") and dataset.description:
            desc_len = len(dataset.description)
            stats["description_statistics"]["with_description"] += 1
            description_lengths.append(desc_len)
            stats["description_statistics"]["max_description_length"] = max(
                stats["description_statistics"]["max_description_length"], desc_len
            )
            stats["description_statistics"]["min_description_length"] = min(
                stats["description_statistics"]["min_description_length"], desc_len
            )

    # Calculate averages
    if description_lengths:
        stats["description_statistics"]["average_description_length"] = sum(
            description_lengths
        ) / len(description_lengths)
    else:
        stats["description_statistics"]["min_description_length"] = 0

    # Convert set to count
    stats["unique_categories"] = len(stats["categories"])
    stats["categories"] = list(stats["categories"])

    logger.info("Created statistics for %d datasets", len(datasets))

    return stats


def validate_dataset_attributes(
    dataset: Any,
    required_attrs: Optional[List[str]] = None,
    optional_attrs: Optional[List[str]] = None,
) -> Tuple[bool, List[str]]:
    """Validate that a dataset object has required and optional attributes.

    Checks a dataset object for the presence of specified attributes,
    useful for ensuring data quality and completeness.

    Args:
        dataset: The dataset object to validate.
        required_attrs: List of attribute names that must be present.
        optional_attrs: List of attribute names that should be present (warnings).

    Returns:
        Tuple of (is_valid, list_of_missing_required_attributes).

    Example:
        >>> from medical_data.browser import MedicalDataset
        >>> dataset = MedicalDataset(name="Test", category="Imaging")
        >>> is_valid, missing = validate_dataset_attributes(
        ...     dataset,
        ...     required_attrs=["name", "category"]
        ... )
        >>> print(is_valid)
        True
    """
    if required_attrs is None:
        required_attrs = ["name", "category"]

    if optional_attrs is None:
        optional_attrs = ["description", "paper_url", "access_url"]

    missing_required: List[str] = []
    missing_optional: List[str] = []

    # Check required attributes
    for attr in required_attrs:
        if not hasattr(dataset, attr) or getattr(dataset, attr) is None:
            missing_required.append(attr)

    # Check optional attributes (for warnings)
    for attr in optional_attrs:
        if not hasattr(dataset, attr) or getattr(dataset, attr) is None:
            missing_optional.append(attr)

    is_valid = len(missing_required) == 0

    if missing_optional:
        logger.warning(
            "Dataset '%s' missing optional attributes: %s",
            getattr(dataset, "name", "Unknown"),
            ", ".join(missing_optional),
        )

    if not is_valid:
        logger.error(
            "Dataset validation failed. Missing required attributes: %s",
            ", ".join(missing_required),
        )

    return is_valid, missing_required


def export_datasets_to_json(
    datasets: List[Any],
    output_path: Union[str, Path],
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """Export a list of datasets to a JSON file.

    Serializes dataset objects to JSON format and saves to a file,
    with proper error handling and logging.

    Args:
        datasets: List of MedicalDataset objects to export.
        output_path: Path where the JSON file will be written.
        indent: Number of spaces for JSON indentation.
        ensure_ascii: If True, escape non-ASCII characters.

    Raises:
        TypeError: If datasets is not a list.
        IOError: If there's an error writing the file.
        ValueError: If a dataset cannot be serialized.

    Example:
        >>> from medical_data.browser import MedicalDataset
        >>> datasets = [MedicalDataset(name="Test", category="Imaging")]
        >>> export_datasets_to_json(datasets, "output.json")
    """
    if not isinstance(datasets, list):
        raise TypeError(f"datasets must be a list, got {type(datasets)}")

    output_path = Path(output_path)

    # Prepare data for serialization
    serializable_data = []
    for dataset in datasets:
        try:
            if hasattr(dataset, "to_dict"):
                serializable_data.append(dataset.to_dict())
            else:
                # Fallback: extract common attributes
                dataset_dict = {
                    "name": getattr(dataset, "name", None),
                    "category": getattr(dataset, "category", None),
                    "description": getattr(dataset, "description", None),
                    "paper_url": getattr(dataset, "paper_url", None),
                    "access_url": getattr(dataset, "access_url", None),
                    "data_url": getattr(dataset, "data_url", None),
                    "requires_registration": getattr(
                        dataset, "requires_registration", False