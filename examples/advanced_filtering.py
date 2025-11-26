#!/usr/bin/env python3
"""Advanced filtering examples for medical data browser.

This module demonstrates advanced filtering techniques and patterns for working
with medical datasets. It showcases complex queries, multi-criteria filtering,
custom filter functions, and data analysis workflows.

Examples include:
- Complex multi-criteria filtering
- Custom predicate functions
- Chaining multiple filters
- Statistical analysis on filtered results
- Category-based filtering patterns
- URL availability filtering
- Registration requirement filtering
- Text-based search with filters

Usage:
    python examples/advanced_filtering.py

Requirements:
    - medical_data package must be installed
    - README.md with dataset catalog must be present
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from medical_data.browser import MedicalDataBrowser, MedicalDataset
from medical_data.utils import (
    create_summary_statistics,
    filter_datasets,
    format_dataset_output,
    truncate_text,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def example_1_basic_multi_criteria_filtering() -> None:
    """Example 1: Basic multi-criteria filtering with AND logic.
    
    Demonstrates how to filter datasets based on multiple criteria
    that all must be satisfied simultaneously.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Multi-Criteria Filtering (AND Logic)")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Filter for datasets that:
    # - Are in Medical Imaging Data category
    # - Do NOT require registration
    criteria = {
        "category": "Medical Imaging Data",
        "requires_registration": False,
    }
    
    filtered = filter_datasets(browser.datasets, criteria, match_all=True)
    
    print(f"\nFound {len(filtered)} imaging datasets without registration requirements")
    print("\nFirst 3 results:")
    for dataset in filtered[:3]:
        print(format_dataset_output(dataset, detailed=False))
        print("-" * 40)


def example_2_or_logic_filtering() -> None:
    """Example 2: OR logic filtering for flexible matching.
    
    Shows how to find datasets matching any of several criteria,
    useful for broad searches across categories or types.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: OR Logic Filtering")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Filter for datasets in either of these categories
    imaging_categories = [
        "Medical Imaging Data",
        "Challenges",
    ]
    
    results = []
    for category in imaging_categories:
        category_datasets = browser.browse_by_category(category)
        results.extend(category_datasets)
    
    print(f"\nFound {len(results)} datasets across imaging-related categories")
    
    # Get statistics on the combined results
    stats = create_summary_statistics(results)
    print(f"\nCategory breakdown:")
    for cat, count in stats["category_counts"].items():
        print(f"  {cat}: {count} datasets")


def example_3_custom_predicate_functions() -> None:
    """Example 3: Using custom predicate functions for advanced filtering.
    
    Demonstrates how to use lambda functions and custom predicates
    for complex filtering logic that goes beyond simple equality.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Custom Predicate Functions")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Filter for datasets with long descriptions (>200 characters)
    criteria = {
        "description": lambda desc: len(desc) > 200,
    }
    
    filtered = filter_datasets(browser.datasets, criteria, match_all=True)
    
    print(f"\nFound {len(filtered)} datasets with detailed descriptions (>200 chars)")
    print("\nSample dataset with detailed description:")
    if filtered:
        dataset = filtered[0]
        print(format_dataset_output(dataset, detailed=True))


def example_4_url_availability_filtering() -> None:
    """Example 4: Filter by URL and access information availability.
    
    Shows how to find datasets based on what types of URLs and
    access information are available.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: URL Availability Filtering")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Find datasets with both paper and direct data access
    criteria = {
        "paper_url": lambda url: url is not None,
        "data_url": lambda url: url is not None,
    }
    
    filtered = filter_datasets(browser.datasets, criteria, match_all=True)
    
    print(f"\nFound {len(filtered)} datasets with both paper and data URLs")
    print("\nFirst 3 results:")
    for dataset in filtered[:3]:
        print(f"\nName: {dataset.name}")
        print(f"Paper: {dataset.paper_url}")
        print(f"Data: {dataset.data_url}")
        print("-" * 40)


def example_5_registration_free_datasets() -> None:
    """Example 5: Find all freely accessible datasets.
    
    Identifies datasets that don't require registration,
    useful for quick-start projects and prototyping.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Registration-Free Datasets")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Filter for datasets that don't require registration
    # and have access URLs
    criteria = {
        "requires_registration": False,
        "access_url": lambda url: url is not None,
    }
    
    filtered = filter_datasets(browser.datasets, criteria, match_all=True)
    
    print(f"\nFound {len(filtered)} freely accessible datasets with URLs")
    
    # Group by category
    category_groups: Dict[str, List[MedicalDataset]] = {}
    for dataset in filtered:
        if dataset.category not in category_groups:
            category_groups[dataset.category] = []
        category_groups[dataset.category].append(dataset)
    
    print("\nBreakdown by category:")
    for category, datasets in sorted(category_groups.items()):
        print(f"\n{category}: {len(datasets)} datasets")
        for dataset in datasets[:2]:  # Show first 2 per category
            print(f"  - {dataset.name}")


def example_6_text_search_with_filters() -> None:
    """Example 6: Combining text search with filtering criteria.
    
    Shows how to perform keyword searches and then apply
    additional filters to refine results.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Text Search with Additional Filters")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # First, search for "brain" related datasets
    search_results = browser.search_datasets("brain", case_sensitive=False)
    print(f"\nInitial search for 'brain': {len(search_results)} results")
    
    # Then filter for those with papers
    criteria = {
        "paper_url": lambda url: url is not None,
    }
    
    filtered = filter_datasets(search_results, criteria, match_all=True)
    
    print(f"After filtering for datasets with papers: {len(filtered)} results")
    print("\nResults:")
    for dataset in filtered[:5]:
        print(f"\n{dataset.name}")
        print(f"  Category: {dataset.category}")
        print(f"  Paper: {dataset.paper_url}")
        desc = truncate_text(dataset.description, max_length=100)
        print(f"  Description: {desc}")


def example_7_complex_chained_filtering() -> None:
    """Example 7: Complex chained filtering workflow.
    
    Demonstrates a multi-step filtering process that progressively
    narrows down results based on different criteria.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Complex Chained Filtering")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    print(f"\nStarting with {len(browser.datasets)} total datasets")
    
    # Step 1: Filter by category
    step1 = browser.browse_by_category("Medical Imaging Data")
    print(f"Step 1 - Imaging datasets: {len(step1)} datasets")
    
    # Step 2: Filter for those with papers
    criteria_step2 = {
        "paper_url": lambda url: url is not None,
    }
    step2 = filter_datasets(step1, criteria_step2, match_all=True)
    print(f"Step 2 - With papers: {len(step2)} datasets")
    
    # Step 3: Filter for those without registration
    criteria_step3 = {
        "requires_registration": False,
    }
    step3 = filter_datasets(step2, criteria_step3, match_all=True)
    print(f"Step 3 - No registration required: {len(step3)} datasets")
    
    # Step 4: Filter for those with substantial descriptions
    criteria_step4 = {
        "description": lambda desc: len(desc) > 100,
    }
    final_results = filter_datasets(step3, criteria_step4, match_all=True)
    print(f"Step 4 - With detailed descriptions: {len(final_results)} datasets")
    
    print("\nFinal filtered datasets:")
    for dataset in final_results[:3]:
        print(format_dataset_output(dataset, detailed=False))
        print("-" * 40)


def example_8_statistical_analysis_on_filtered_data() -> None:
    """Example 8: Performing statistical analysis on filtered datasets.
    
    Shows how to generate comprehensive statistics on a filtered
    subset of datasets for analysis and reporting.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Statistical Analysis on Filtered Data")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Filter for datasets with full metadata
    criteria = {
        "paper_url": lambda url: url is not None,
        "access_url": lambda url: url is not None,
        "description": lambda desc: len(desc) > 50,
    }
    
    well_documented = filter_datasets(browser.datasets, criteria, match_all=True)
    
    print(f"\nAnalyzing {len(well_documented)} well-documented datasets")
    
    # Generate statistics
    stats = create_summary_statistics(well_documented)
    
    print("\nStatistical Summary:")
    print(f"  Total datasets: {stats['total_datasets']}")
    print(f"  Unique categories: {stats['unique_categories']}")
    print(f"  Datasets with papers: {stats['datasets_with_papers']}")
    print(f"  Datasets requiring registration: {stats['datasets_requiring_registration']}")
    
    print("\nDescription Statistics:")
    desc_stats = stats['description_statistics']
    print(f"  Datasets with descriptions: {desc_stats['with_description']}")
    print(f"  Average description length: {desc_stats['average_description_length']:.1f} chars")
    print(f"  Max description length: {desc_stats['max_description_length']} chars")
    print(f"  Min description length: {desc_stats['min_description_length']} chars")
    
    print("\nURL Statistics:")
    url_stats = stats['url_statistics']
    print(f"  Paper URLs: {url_stats['paper_urls']}")
    print(f"  Access URLs: {url_stats['access_urls']}")
    print(f"  Data URLs: {url_stats['data_urls']}")


def example_9_category_comparison() -> None:
    """Example 9: Compare datasets across different categories.
    
    Demonstrates how to analyze and compare characteristics
    of datasets from different categories.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Category Comparison Analysis")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Get all categories
    categories = browser.list_categories()
    
    print("\nComparing dataset characteristics across categories:")
    print("-" * 80)
    
    comparison_results = []
    
    for category_name, count in categories[:5]:  # Top 5 categories
        category_datasets = browser.browse_by_category(category_name)
        
        # Calculate metrics
        with_papers = sum(1 for d in category_datasets if d.has_paper())
        with_access = sum(1 for d in category_datasets if d.has_access())
        needs_reg = sum(1 for d in category_datasets if d.requires_registration)
        
        comparison_results.append({
            "category": category_name,
            "total": count,
            "with_papers": with_papers,
            "with_access": with_access,
            "needs_registration": needs_reg,
        })
    
    # Display comparison
    for result in comparison_results:
        print(f"\n{result['category']}:")
        print(f"  Total: {result['total']}")
        print(f"  With papers: {result['with_papers']} ({result['with_papers']/result['total']*100:.1f}%)")
        print(f"  With access info: {result['with_access']} ({result['with_access']/result['total']*100:.1f}%)")
        print(f"  Needs registration: {result['needs_registration']} ({result['needs_registration']/result['total']*100:.1f}%)")


def example_10_custom_scoring_and_ranking() -> None:
    """Example 10: Custom scoring system for ranking datasets.
    
    Demonstrates how to create a custom scoring function to rank
    datasets based on multiple quality factors.
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Custom Scoring and Ranking")
    print("=" * 80)
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    def calculate_dataset_score(dataset: MedicalDataset) -> float:
        """Calculate a quality score for a dataset.
        
        Args:
            dataset: The dataset to score.
            
        Returns:
            Quality score (0-100).
        """
        score = 0.0
        
        # Paper availability (30 points)
        if dataset.has_paper():
            score += 30
        
        # Access information (25 points)
        if dataset.has_access():
            score += 25
        
        # No registration required (20 points)
        if not dataset.requires_registration:
            score += 20
        
        # Description quality (25 points based on length)
        desc_length = len(dataset.description)
        if desc_length > 200:
            score += 25
        elif desc_length > 100:
            score