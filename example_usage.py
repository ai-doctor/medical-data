#!/usr/bin/env python3
"""
Example Usage of Medical Data Browser
======================================

This script demonstrates how to use the Medical Data Browser to search,
browse, and analyze medical datasets from the README.md file.

The examples show various use cases including:
- Searching for specific types of datasets (imaging, EHR, challenges)
- Filtering by registration requirements
- Browsing by category
- Exporting results
- Displaying formatted results
"""

from medical_data_browser import MedicalDataBrowser, MedicalDataset
from utils import (
    create_summary_statistics,
    filter_datasets,
    format_dataset_output,
    truncate_text
)
from typing import List
import json


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80 + "\n")


def display_datasets_summary(datasets: List[MedicalDataset], title: str) -> None:
    """Display a summary of datasets."""
    print(f"\n{title}")
    print("-" * len(title))
    print(f"Found {len(datasets)} dataset(s)\n")
    
    for idx, dataset in enumerate(datasets, 1):
        print(f"{idx}. {dataset.name}")
        print(f"   Category: {dataset.category}")
        
        # Show truncated description
        if dataset.description:
            desc = truncate_text(dataset.description, max_length=100)
            print(f"   Description: {desc}")
        
        # Show access information
        if dataset.access_url:
            print(f"   Access: {dataset.access_url}")
        elif dataset.data_url:
            print(f"   Data: {dataset.data_url}")
        
        if dataset.requires_registration:
            print(f"   ⚠️  Registration Required")
        
        print()


def example_1_basic_usage():
    """Example 1: Basic usage - Loading and parsing the README."""
    print_section_header("Example 1: Basic Usage - Loading and Parsing Data")
    
    # Initialize the browser
    browser = MedicalDataBrowser("README.md")
    
    # Parse the README file
    print("Parsing README.md file...")
    browser.parse_readme()
    
    # Display basic statistics
    stats = browser.get_statistics()
    print(f"Successfully loaded {stats['total_datasets']} datasets from {stats['categories']} categories")
    print(f"- Datasets with papers: {stats['datasets_with_papers']}")
    print(f"- Datasets with access links: {stats['datasets_with_access']}")
    print(f"- Datasets requiring registration: {stats['requires_registration']}")


def example_2_search_imaging_data():
    """Example 2: Searching for medical imaging datasets."""
    print_section_header("Example 2: Searching for Medical Imaging Datasets")
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Search for imaging-related datasets
    print("Searching for datasets containing 'MRI'...")
    mri_datasets = browser.search_datasets("MRI")
    display_datasets_summary(mri_datasets, "MRI Datasets")
    
    # Search for CT scan datasets
    print("\nSearching for datasets containing 'CT'...")
    ct_datasets = browser.search_datasets("CT")
    print(f"Found {len(ct_datasets)} CT-related datasets")
    
    # Search for X-ray datasets
    print("\nSearching for datasets containing 'X-ray'...")
    xray_datasets = browser.search_datasets("X-ray")
    print(f"Found {len(xray_datasets)} X-ray-related datasets")


def example_3_browse_by_category():
    """Example 3: Browsing datasets by category."""
    print_section_header("Example 3: Browsing Datasets by Category")
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # List all categories
    print("Available Categories:")
    categories = browser.list_categories()
    for cat, count in categories:
        print(f"  - {cat}: {count} datasets")
    
    # Browse Medical Imaging Data category
    print("\n" + "-"*80)
    print("Browsing 'Medical Imaging Data' category...")
    print("-"*80)
    
    imaging_datasets = browser.browse_by_category("Medical Imaging Data")
    
    # Display first 5 datasets with details
    print(f"\nShowing first 5 of {len(imaging_datasets)} Medical Imaging datasets:\n")
    for dataset in imaging_datasets[:5]:
        browser.display_dataset(dataset, detailed=True)


def example_4_ehr_datasets():
    """Example 4: Finding Electronic Health Record (EHR) datasets."""
    print_section_header("Example 4: Finding EHR Datasets")
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Get EHR category
    ehr_datasets = browser.browse_by_category("Data derived from Electronic Health Records (EHRs)")
    
    display_datasets_summary(ehr_datasets, "Electronic Health Record (EHR) Datasets")
    
    # Display detailed information for MIMIC-III
    print("\nDetailed information for MIMIC-III dataset:")
    mimic = browser.get_dataset_by_name("MIMIC-III, a freely accessible critical care database")
    if mimic:
        browser.display_dataset(mimic)


def example_5_challenges_contests():
    """Example 5: Finding challenge and contest datasets."""
    print_section_header("Example 5: Finding Challenge and Contest Datasets")
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Get challenges category
    challenge_datasets = browser.browse_by_category("Challenges/Contest Data")
    
    print(f"Found {len(challenge_datasets)} challenge/contest datasets\n")
    
    # Search for specific challenge types
    print("Searching for 'Kaggle' challenges...")
    kaggle_challenges = [d for d in challenge_datasets if 'kaggle' in d.name.lower() or 'kaggle' in d.description.lower()]
    display_datasets_summary(kaggle_challenges, "Kaggle Medical Challenges")
    
    print("\nSearching for brain-related challenges...")
    brain_challenges = [d for d in challenge_datasets if 'brain' in d.name.lower() or 'brain' in d.description.lower()]
    display_datasets_summary(brain_challenges, "Brain-Related Challenges")


def example_6_registration_filtering():
    """Example 6: Filtering datasets by registration requirement."""
    print_section_header("Example 6: Filtering by Registration Requirement")
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Find datasets that don't require registration
    no_reg_datasets = [d for d in browser.datasets if not d.requires_registration]
    print(f"Datasets NOT requiring registration: {len(no_reg_datasets)}")
    
    # Find datasets that require registration
    reg_datasets = [d for d in browser.datasets if d.requires_registration]
    print(f"Datasets requiring registration: {len(reg_datasets)}")
    
    # Show first 5 datasets without registration requirement
    print("\nFirst 5 datasets with immediate access (no registration):")
    for idx, dataset in enumerate(no_reg_datasets[:5], 1):
        print(f"\n{idx}. {dataset.name}")
        print(f"   Category: {dataset.category}")
        if dataset.access_url:
            print(f"   Access: {dataset.access_url}")


def example_7_disease_specific_search():
    """Example 7: Searching for disease-specific datasets."""
    print_section_header("Example 7: Searching for Disease-Specific Datasets")
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    diseases = ["cancer", "alzheimer", "diabetes", "heart", "lung"]
    
    print("Searching for disease-specific datasets:\n")
    
    for disease in diseases:
        datasets = browser.search_datasets(disease)
        print(f"{disease.upper()}: {len(datasets)} dataset(s)")
        
        if datasets:
            # Show names of datasets found
            for dataset in datasets[:3]:  # Show first 3
                print(f"  - {dataset.name}")
            
            if len(datasets) > 3:
                print(f"  ... and {len(datasets) - 3} more")
        
        print()


def example_8_export_filtered_results():
    """Example 8: Exporting filtered results."""
    print_section_header("Example 8: Exporting Filtered Results")
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    # Search for cancer-related datasets
    cancer_datasets = browser.search_datasets("cancer")
    
    print(f"Found {len(cancer_datasets)} cancer-related datasets")
    print("Exporting to JSON file...")
    
    # Create export data
    export_data = {
        'query': 'cancer',
        'total_results': len(cancer_datasets),
        'datasets': [
            {
                'name': d.name,
                'category': d.category,
                'description': d.description,
                'paper_url': d.paper_url,
                'access_url': d.access_url,
                'data_url': d.data_url,
                'requires_registration': d.requires_registration
            }
            for d in cancer_datasets
        ]
    }
    
    # Export to file
    output_file = "cancer_datasets.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully exported to {output_file}")
    
    # Also export all datasets
    print("\nExporting all datasets...")
    browser.export_to_json("all_medical_datasets.json")


def example_9_category_statistics():
    """Example 9: Analyzing category statistics."""
    print_section_header("Example 9: Category Statistics and Analysis")
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    stats = browser.get_statistics()
    
    print("Category Breakdown:\n")
    
    # Sort categories by dataset count
    sorted_categories = sorted(
        stats['category_breakdown'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    for category, count in sorted_categories:
        percentage = (count / stats['total_datasets']) * 100
        bar = "█" * int(percentage / 2)  # Visual bar
        print(f"{category:50s} {count:3d} ({percentage:5.1f}%) {bar}")
    
    print("\nDataset Access Statistics:")
    print(f"- With papers: {stats['datasets_with_papers']} ({stats['datasets_with_papers']/stats['total_datasets']*100:.1f}%)")
    print(f"- With access links: {stats['datasets_with_access']} ({stats['datasets_with_access']/stats['total_datasets']*100:.1f}%)")
    print(f"- Requiring registration: {stats['requires_registration']} ({stats['requires_registration']/stats['total_datasets']*100:.1f}%)")


def example_10_comprehensive_search():
    """Example 10: Comprehensive search with multiple criteria."""
    print_section_header("Example 10: Comprehensive Multi-Criteria Search")
    
    browser = MedicalDataBrowser("README.md")
    browser.parse_readme()
    
    print("Searching for: Brain imaging datasets that don't require registration\n")
    
    # Step 1: Search for brain-related datasets
    brain_datasets = browser.search_datasets("brain")
    print(f"Step 1: Found {len(brain_datasets)} brain-related datasets")
    
    # Step 2: Filter for imaging category
    imaging_brain = [d for d in brain_datasets if "imaging" in d.category.lower()]
    print(f"Step 2: Filtered to {len(imaging_brain)} brain imaging datasets")
    
    # Step 3: Filter out those requiring registration
    no_reg_brain_imaging = [d for d in imaging_brain if not d.requires_registration]
    print(f"Step 3: Filtered to {len(no_reg_brain_imaging)} datasets without registration requirement\n")
    
    # Display results
    display_datasets_summary(no_reg_brain_imaging, "Brain Imaging Datasets (No Registration Required)")


def main():
    """Run all examples."""
    print("\n" + "="*80)
    print(" Medical Data Browser - Example Usage Scripts")
    print("="*80)
    print("\nThis script demonstrates various use cases for the Medical Data Browser.")
    print("You can run individual examples or all of them.\n")
    
    examples = [
        ("Basic Usage", example_1_basic_usage),
        ("Search Imaging Data", example_2_search_imaging_data),
        ("Browse by Category", example_3_browse_by_category),
        ("EHR Datasets", example_4_ehr_datasets),
        ("Challenges and Contests", example_5_challenges_contests),
        ("Registration Filtering", example_6_registration_filtering),
        ("Disease-Specific Search", example_7_disease_specific_search),
        ("Export Results", example_8_export_filtered_results),
        ("Category Statistics", example_9_category_statistics),
        ("Comprehensive Search", example_10_comprehensive_search),
    ]
    
    print("Available Examples:")
    for idx, (name, _) in enumerate(examples, 1):
        print(f"{idx:2d}. {name}")
    print(f" 0. Run all examples")
    
    try:
        choice = input("\nEnter example number to run (0 for all): ").strip()
        
        if choice == "0":
            # Run all examples
            for name, func in examples:
                func()
                input("\nPress Enter to continue to next example...")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                examples[idx][1]()
            else:
                print("Invalid choice!")
    except (ValueError, KeyboardInterrupt):
        print("\nExiting...")


if __name__ == "__main__":
    main()