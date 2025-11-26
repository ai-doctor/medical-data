"""Command-line interface for the medical data browser.

This module provides a CLI entry point for browsing, searching, and analyzing
medical datasets. It wraps the MedicalDataBrowser functionality with a
user-friendly command-line interface.

Usage:
    python -m medical_data search "MRI brain"
    python -m medical_data list-categories
    python -m medical_data browse --category "Medical Imaging Data"
    python -m medical_data stats
    python -m medical_data export --output datasets.json

The module follows PEP 8 standards and includes comprehensive error handling,
logging, and help documentation for production use.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional

from medical_data.browser import MedicalDataBrowser
from medical_data.utils import (
    create_summary_statistics,
    export_datasets_to_json,
    format_dataset_output,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Version information
__version__ = "1.0.0"


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance with all commands and options.
    """
    parser = argparse.ArgumentParser(
        prog="medical-data",
        description=(
            "Medical Data Browser - Browse, search, and analyze medical datasets "
            "for machine learning applications"
        ),
        epilog=(
            "For more information, visit: "
            "https://github.com/ai-doctor/medical-data"
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show program version and exit",
    )

    parser.add_argument(
        "--readme",
        type=str,
        default="README.md",
        help="Path to the README.md file containing dataset catalog (default: README.md)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress all non-error output",
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=False,
    )

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search for datasets by keyword",
        description="Search for medical datasets matching a query string",
    )
    search_parser.add_argument(
        "query",
        type=str,
        help="Search query (searches in name and description)",
    )
    search_parser.add_argument(
        "--case-sensitive",
        action="store_true",
        help="Perform case-sensitive search",
    )
    search_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed information for each result",
    )
    search_parser.add_argument(
        "--no-urls",
        action="store_true",
        help="Hide URLs in output",
    )

    # Browse command
    browse_parser = subparsers.add_parser(
        "browse",
        help="Browse datasets by category",
        description="Browse medical datasets filtered by category",
    )
    browse_parser.add_argument(
        "--category",
        "-c",
        type=str,
        required=True,
        help="Category name to browse",
    )
    browse_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed information for each dataset",
    )
    browse_parser.add_argument(
        "--no-urls",
        action="store_true",
        help="Hide URLs in output",
    )

    # List categories command
    list_parser = subparsers.add_parser(
        "list-categories",
        help="List all available categories",
        description="Display all dataset categories with counts",
    )
    list_parser.add_argument(
        "--sort-by",
        choices=["name", "count"],
        default="count",
        help="Sort categories by name or count (default: count)",
    )

    # Statistics command
    stats_parser = subparsers.add_parser(
        "stats",
        help="Show dataset statistics",
        description="Display comprehensive statistics about the dataset catalog",
    )
    stats_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    stats_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Save statistics to file (only for JSON format)",
    )

    # Get dataset command
    get_parser = subparsers.add_parser(
        "get",
        help="Get information about a specific dataset",
        description="Retrieve detailed information about a specific dataset by name",
    )
    get_parser.add_argument(
        "name",
        type=str,
        help="Dataset name (supports partial matching)",
    )
    get_parser.add_argument(
        "--exact",
        action="store_true",
        help="Require exact name match",
    )
    get_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    # Export command
    export_parser = subparsers.add_parser(
        "export",
        help="Export datasets to JSON file",
        description="Export all or filtered datasets to a JSON file",
    )
    export_parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Output JSON file path",
    )
    export_parser.add_argument(
        "--category",
        "-c",
        type=str,
        help="Export only datasets from this category",
    )
    export_parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2)",
    )

    return parser


def handle_search(
    browser: MedicalDataBrowser,
    args: argparse.Namespace,
) -> int:
    """Handle the search command.

    Args:
        browser: Initialized MedicalDataBrowser instance.
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        results = browser.search_datasets(
            args.query,
            case_sensitive=args.case_sensitive,
        )

        if not results:
            print(f"No datasets found matching '{args.query}'")
            return 0

        print(f"\nFound {len(results)} dataset(s) matching '{args.query}':\n")

        for i, dataset in enumerate(results, 1):
            print(f"{i}. {'-' * 70}")
            output = format_dataset_output(
                dataset,
                detailed=args.detailed,
                include_urls=not args.no_urls,
            )
            print(output)
            print()

        return 0

    except Exception as e:
        logger.error("Error during search: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_browse(
    browser: MedicalDataBrowser,
    args: argparse.Namespace,
) -> int:
    """Handle the browse command.

    Args:
        browser: Initialized MedicalDataBrowser instance.
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        results = browser.browse_by_category(args.category)

        if not results:
            print(f"No datasets found in category '{args.category}'")
            print("\nUse 'medical-data list-categories' to see available categories")
            return 0

        print(f"\nFound {len(results)} dataset(s) in category '{args.category}':\n")

        for i, dataset in enumerate(results, 1):
            print(f"{i}. {'-' * 70}")
            output = format_dataset_output(
                dataset,
                detailed=args.detailed,
                include_urls=not args.no_urls,
            )
            print(output)
            print()

        return 0

    except Exception as e:
        logger.error("Error during browse: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_list_categories(
    browser: MedicalDataBrowser,
    args: argparse.Namespace,
) -> int:
    """Handle the list-categories command.

    Args:
        browser: Initialized MedicalDataBrowser instance.
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        categories = browser.list_categories()

        if not categories:
            print("No categories found")
            return 0

        # Sort by name if requested
        if args.sort_by == "name":
            categories = sorted(categories, key=lambda x: x[0])

        print(f"\nFound {len(categories)} categor{'y' if len(categories) == 1 else 'ies'}:\n")

        # Calculate column width for alignment
        max_name_len = max(len(name) for name, _ in categories)

        for name, count in categories:
            print(f"  {name:<{max_name_len}}  {count:>4} dataset(s)")

        print()
        return 0

    except Exception as e:
        logger.error("Error listing categories: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_stats(
    browser: MedicalDataBrowser,
    args: argparse.Namespace,
) -> int:
    """Handle the stats command.

    Args:
        browser: Initialized MedicalDataBrowser instance.
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        stats = browser.get_statistics()

        if args.format == "json":
            json_output = json.dumps(stats, indent=2, ensure_ascii=False)

            if args.output:
                output_path = Path(args.output)
                output_path.write_text(json_output, encoding="utf-8")
                print(f"Statistics saved to: {output_path}")
            else:
                print(json_output)

        else:
            # Text format
            print("\n" + "=" * 70)
            print("MEDICAL DATASET CATALOG STATISTICS")
            print("=" * 70 + "\n")

            print(f"Total Datasets:                    {stats['total_datasets']}")
            print(f"Total Categories:                  {stats['categories']}")
            print(f"Datasets with Papers:              {stats['datasets_with_papers']}")
            print(f"Datasets with Access Info:         {stats['datasets_with_access']}")
            print(f"Datasets Requiring Registration:   {stats['datasets_requiring_registration']}")

            print("\nCategory Distribution:")
            categories = stats.get("category_distribution", {})
            if categories:
                max_name_len = max(len(name) for name in categories.keys())
                for name, count in sorted(
                    categories.items(),
                    key=lambda x: x[1],
                    reverse=True,
                ):
                    percentage = (count / stats['total_datasets']) * 100
                    print(f"  {name:<{max_name_len}}  {count:>4} ({percentage:>5.1f}%)")

            print("\nURL Statistics:")
            url_stats = stats.get("url_statistics", {})
            if url_stats:
                print(f"  Paper URLs:         {url_stats.get('paper_urls', 0)}")
                print(f"  Access URLs:        {url_stats.get('access_urls', 0)}")
                print(f"  Data URLs:          {url_stats.get('data_urls', 0)}")
                print(f"  Information URLs:   {url_stats.get('information_urls', 0)}")
                print(f"  Overview URLs:      {url_stats.get('overview_urls', 0)}")

            print()

        return 0

    except Exception as e:
        logger.error("Error generating statistics: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_get(
    browser: MedicalDataBrowser,
    args: argparse.Namespace,
) -> int:
    """Handle the get command.

    Args:
        browser: Initialized MedicalDataBrowser instance.
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        dataset = browser.get_dataset_by_name(args.name, exact_match=args.exact)

        if not dataset:
            print(f"Dataset not found: '{args.name}'")
            if not args.exact:
                print("\nTry using --exact for exact name matching")
            return 1

        if args.format == "json":
            json_output = json.dumps(dataset.to_dict(), indent=2, ensure_ascii=False)
            print(json_output)
        else:
            print("\n" + "=" * 70)
            output = format_dataset_output(dataset, detailed=True, include_urls=True)
            print(output)
            print("=" * 70 + "\n")

        return 0

    except Exception as e:
        logger.error("Error retrieving dataset: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_export(
    browser: MedicalDataBrowser,
    args: argparse.Namespace,
) -> int:
    """Handle the export command.

    Args:
        browser: Initialized MedicalDataBrowser instance.
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        # Get datasets to export
        if args.category:
            datasets = browser.browse_by_category(args.category)
            if not datasets:
                print(f"No datasets found in category '{args.category}'")
                return 1
        else:
            datasets = browser.datasets

        # Export to JSON
        export_datasets_to_json(
            datasets,
            args.output,
            indent=args.indent,
        )

        print(f"Exported {len(datasets)} dataset(s) to: {args.output}")
        return 0

    except Exception as e:
        logger.error("Error exporting datasets: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI application.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Configure logging level
    if args.verbose:
        logging.