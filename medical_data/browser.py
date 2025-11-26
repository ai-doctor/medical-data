"""Medical data browser module.

This module provides functionality to parse, search, browse, and analyze medical datasets
cataloged in markdown files. It includes a comprehensive browser for medical machine learning
datasets with support for various data types including medical imaging, EHR data, challenges,
and biomedical literature.

The module follows PEP 8 standards and includes comprehensive type hints, docstrings,
error handling, and logging for production use.

Example:
    Basic usage of the medical data browser:

    >>> from medical_data.browser import MedicalDataBrowser
    >>> browser = MedicalDataBrowser("README.md")
    >>> browser.parse_readme()
    >>> datasets = browser.search_datasets("MRI")
    >>> stats = browser.get_statistics()
    >>> print(f"Found {len(datasets)} MRI datasets")

Attributes:
    logger (logging.Logger): Module-level logger for browser operations.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure module logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class MedicalDataset:
    """Represents a medical dataset with associated metadata.

    This class encapsulates all information about a medical dataset including
    its name, category, description, URLs, and access requirements.

    Attributes:
        name: The name of the dataset.
        category: The category the dataset belongs to (e.g., "Medical Imaging Data").
        description: Detailed description of the dataset.
        paper_url: URL to the associated research paper, if available.
        access_url: URL to access the dataset, if available.
        data_url: Direct URL to download data, if available.
        information_url: URL for general information, if available.
        overview_url: URL for dataset overview, if available.
        requires_registration: Whether the dataset requires registration to access.
        raw_text: Original unparsed text from the source.
    """

    name: str
    category: str
    description: str = ""
    paper_url: Optional[str] = None
    access_url: Optional[str] = None
    data_url: Optional[str] = None
    information_url: Optional[str] = None
    overview_url: Optional[str] = None
    requires_registration: bool = False
    raw_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the dataset to a dictionary representation.

        Returns:
            A dictionary containing all dataset attributes.
        """
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "paper_url": self.paper_url,
            "access_url": self.access_url,
            "data_url": self.data_url,
            "information_url": self.information_url,
            "overview_url": self.overview_url,
            "requires_registration": self.requires_registration,
        }

    def has_paper(self) -> bool:
        """Check if the dataset has an associated paper.

        Returns:
            True if a paper URL is available, False otherwise.
        """
        return self.paper_url is not None

    def has_access(self) -> bool:
        """Check if the dataset has access information.

        Returns:
            True if any access URL is available, False otherwise.
        """
        return any(
            [
                self.access_url,
                self.data_url,
                self.information_url,
                self.overview_url,
            ]
        )


class MedicalDataBrowser:
    """Browser for medical machine learning datasets.

    This class provides comprehensive functionality to parse, search, browse,
    and analyze medical datasets from markdown-formatted catalog files. It supports
    multiple data categories, advanced filtering, and export capabilities.

    The browser parses structured markdown files containing dataset information
    and provides a programmatic interface for discovering and analyzing datasets.

    Attributes:
        readme_path: Path to the markdown file containing dataset catalog.
        datasets: List of parsed MedicalDataset objects.

    Example:
        >>> browser = MedicalDataBrowser("README.md")
        >>> browser.parse_readme()
        >>> imaging_datasets = browser.browse_by_category("Medical Imaging Data")
        >>> print(f"Found {len(imaging_datasets)} imaging datasets")
    """

    def __init__(self, readme_path: str) -> None:
        """Initialize the medical data browser.

        Args:
            readme_path: Path to the markdown file containing the dataset catalog.

        Raises:
            FileNotFoundError: If the readme file does not exist.
        """
        self.readme_path = Path(readme_path)
        if not self.readme_path.exists():
            error_msg = f"README file not found: {readme_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        self.datasets: List[MedicalDataset] = []
        logger.info("Initialized MedicalDataBrowser with file: %s", readme_path)

    def parse_readme(self) -> None:
        """Parse the README markdown file and extract dataset information.

        This method reads the markdown file, identifies categories and individual
        datasets, extracts metadata, and populates the internal dataset list.

        Raises:
            IOError: If there's an error reading the file.
            ValueError: If the file format is invalid.
        """
        try:
            with open(self.readme_path, encoding="utf-8") as f:
                content = f.read()
            logger.info("Successfully read README file")
        except IOError as e:
            error_msg = f"Error reading README file: {e}"
            logger.error(error_msg)
            raise IOError(error_msg) from e

        # Split content into sections
        lines = content.split("\n")
        current_category = ""
        current_dataset_lines: List[str] = []
        in_dataset = False

        for line in lines:
            # Check for category header (## N. Category Name)
            category_match = re.match(r"^##\s+\d+\.\s+(.+)$", line.strip())
            if category_match:
                # Save previous dataset if exists
                if current_dataset_lines and current_category:
                    self._parse_dataset_section(current_dataset_lines, current_category)
                current_category = category_match.group(1).strip()
                current_dataset_lines = []
                in_dataset = False
                logger.debug("Found category: %s", current_category)
                continue

            # Check for dataset separator
            if line.strip() == "***":
                if current_dataset_lines and current_category:
                    self._parse_dataset_section(current_dataset_lines, current_category)
                current_dataset_lines = []
                in_dataset = False
                continue

            # Check for dataset start (bold text with __)
            if line.strip().startswith("__") and current_category:
                # Save previous dataset if exists
                if current_dataset_lines:
                    self._parse_dataset_section(current_dataset_lines, current_category)
                current_dataset_lines = [line]
                in_dataset = True
                continue

            # Accumulate dataset lines
            if in_dataset and line.strip():
                current_dataset_lines.append(line)

        # Handle last dataset
        if current_dataset_lines and current_category:
            self._parse_dataset_section(current_dataset_lines, current_category)

        logger.info(
            "Parsing complete. Found %d datasets across %d categories",
            len(self.datasets),
            len(self.list_categories()),
        )

    def _parse_dataset_section(self, lines: List[str], category: str) -> None:
        """Parse a section of lines representing a single dataset.

        Args:
            lines: List of lines containing dataset information.
            category: The category this dataset belongs to.
        """
        if not lines:
            return

        # Extract dataset name from first line (remove __ formatting)
        name_line = lines[0].strip()
        name = re.sub(r"__(.+?)__", r"\1", name_line)

        # Initialize metadata
        description_lines: List[str] = []
        paper_url: Optional[str] = None
        access_url: Optional[str] = None
        data_url: Optional[str] = None
        information_url: Optional[str] = None
        overview_url: Optional[str] = None
        requires_registration = False

        # Parse remaining lines
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            # Check for registration requirement
            if "requires registration" in line.lower():
                requires_registration = True

            # Extract URLs by prefix
            line_lower = line.lower()
            if line_lower.startswith("paper:"):
                paper_url = self._extract_url(line)
            elif line_lower.startswith("access:"):
                access_url = self._extract_url(line)
            elif line_lower.startswith("data:"):
                data_url = self._extract_url(line)
            elif line_lower.startswith("information:"):
                information_url = self._extract_url(line)
            elif line_lower.startswith("overview:"):
                overview_url = self._extract_url(line)
            else:
                # It's part of the description
                # Remove markdown formatting
                clean_line = self._clean_markdown(line)
                if clean_line:
                    description_lines.append(clean_line)

        # Create dataset object
        dataset = MedicalDataset(
            name=name,
            category=category,
            description=" ".join(description_lines),
            paper_url=paper_url,
            access_url=access_url,
            data_url=data_url,
            information_url=information_url,
            overview_url=overview_url,
            requires_registration=requires_registration,
            raw_text="\n".join(lines),
        )

        self.datasets.append(dataset)
        logger.debug("Parsed dataset: %s", name)

    def _extract_url(self, text: str) -> Optional[str]:
        """Extract URL from text.

        Args:
            text: Text potentially containing a URL.

        Returns:
            The extracted URL or None if not found.
        """
        url_pattern = re.compile(r"https?://[^\s\)]+")
        match = url_pattern.search(text)
        return match.group(0) if match else None

    def _clean_markdown(self, text: str) -> str:
        """Remove markdown formatting from text.

        Args:
            text: Text with markdown formatting.

        Returns:
            Clean text without markdown syntax.
        """
        # Remove bold
        text = re.sub(r"__(.+?)__", r"\1", text)
        # Remove italic
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"_(.+?)_", r"\1", text)
        # Remove code
        text = re.sub(r"`(.+?)`", r"\1", text)
        # Convert markdown links to just text
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
        return text.strip()

    def search_datasets(self, query: str, case_sensitive: bool = False) -> List[MedicalDataset]:
        """Search for datasets matching a query string.

        The search is performed across dataset names and descriptions.

        Args:
            query: The search query string.
            case_sensitive: Whether to perform case-sensitive search.

        Returns:
            List of datasets matching the query.

        Example:
            >>> browser = MedicalDataBrowser("README.md")
            >>> browser.parse_readme()
            >>> results = browser.search_datasets("brain MRI")
        """
        if not case_sensitive:
            query = query.lower()

        results: List[MedicalDataset] = []
        for dataset in self.datasets:
            search_text = f"{dataset.name} {dataset.description}"
            if not case_sensitive:
                search_text = search_text.lower()

            if query in search_text:
                results.append(dataset)

        logger.info("Search for '%s' found %d results", query, len(results))
        return results

    def browse_by_category(self, category: str) -> List[MedicalDataset]:
        """Get all datasets in a specific category.

        Args:
            category: The category name to filter by.

        Returns:
            List of datasets in the specified category.

        Example:
            >>> browser = MedicalDataBrowser("README.md")
            >>> browser.parse_readme()
            >>> imaging = browser.browse_by_category("Medical Imaging Data")
        """
        results = [d for d in self.datasets if d.category == category]
        logger.info("Category '%s' contains %d datasets", category, len(results))
        return results

    def list_categories(self) -> List[Tuple[str, int]]:
        """List all available categories with dataset counts.

        Returns:
            List of tuples containing (category_name, dataset_count).

        Example:
            >>> browser = MedicalDataBrowser("README.md")
            >>> browser.parse_readme()
            >>> categories = browser.list_categories()
            >>> for name, count in categories:
            ...     print(f"{name}: {count} datasets")
        """
        category_counts: Dict[str, int] = {}
        for dataset in self.datasets:
            category_counts[dataset.category] = category_counts.get(dataset.category, 0) + 1

        return sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    def get_dataset_by_name(self, name: str, exact_match: bool = False) -> Optional[MedicalDataset]:
        """Retrieve a dataset by its name.

        Args:
            name: The dataset name to search for.
            exact_match: If True, requires exact name match (case-insensitive).

        Returns:
            The matching dataset or None if not found.

        Example:
            >>> browser = MedicalDataBrowser("README.md")
            >>> browser.parse_readme()
            >>> dataset = browser.get_dataset_by_name("MIMIC-III")
        """
        name_lower = name.lower()

        for dataset in self.datasets:
            if exact_match:
                if dataset.name.lower() == name_lower:
                    return dataset
            else:
                if name_lower in dataset.name.lower():
                    return dataset

        logger.warning("Dataset not found: %s", name)
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the dataset catalog.

        Returns:
            Dictionary containing various statistics including total datasets,
            category breakdown, and access information.

        Example:
            >>> browser = MedicalDataBrowser("README.md")
            >>> browser.parse_readme()
            >>> stats = browser.get_statistics()
            >>> print(f"Total: {stats['total_datasets']}")
        """
        stats: Dict[str, Any] = {
            "total_datasets": len(self.datasets),
            "categories": len(set(d.category for d in self.datasets)),
            "datasets_with_papers": sum(1 for d in self.datasets if d.has_paper()),
            "datasets_with_access": sum(1 for d in self.datasets if d.