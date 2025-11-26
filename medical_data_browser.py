#!/usr/bin/env python3
"""
Medical Data Browser
A tool to parse, categorize, and browse medical datasets from the README.md file.

This script provides functionality to:
- Browse datasets by category
- Search for specific datasets by name or keyword
- Display detailed information about each resource including papers, access links, and descriptions
- Export filtered results to various formats
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import argparse


@dataclass
class MedicalDataset:
    """Represents a medical dataset with all its metadata."""
    name: str
    category: str
    description: str
    paper_url: Optional[str] = None
    access_url: Optional[str] = None
    information_url: Optional[str] = None
    data_url: Optional[str] = None
    requires_registration: bool = False
    additional_info: Optional[str] = None


class MedicalDataBrowser:
    """Main class for parsing and browsing medical datasets."""
    
    CATEGORIES = {
        "1": "Medical Imaging Data",
        "2": "Challenges/Contest Data",
        "3": "Data derived from Electronic Health Records (EHRs)",
        "4": "National Healthcare Data",
        "5": "UCI Datasets",
        "6": "Biomedical Literature",
        "7": "Medical Speech Data"
    }
    
    def __init__(self, readme_path: str = "README.md"):
        """Initialize the browser with the README file path."""
        self.readme_path = readme_path
        self.datasets: List[MedicalDataset] = []
        self.categories_index: Dict[str, List[MedicalDataset]] = defaultdict(list)
        
    def parse_readme(self) -> None:
        """Parse the README.md file and extract all datasets."""
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: {self.readme_path} not found!")
            return
        
        # Split content by main categories
        category_pattern = r'## (\d+)\.\s+(.+?)(?=\n##|\Z)'
        category_matches = re.finditer(category_pattern, content, re.DOTALL)
        
        for match in category_matches:
            category_num = match.group(1)
            category_name = match.group(2).strip()
            category_content = match.group(0)
            
            # Parse individual datasets within each category
            self._parse_category_datasets(category_num, category_name, category_content)
    
    def _parse_category_datasets(self, category_num: str, category_name: str, content: str) -> None:
        """Parse datasets within a specific category."""
        # Split by dataset entries (separated by ***)
        dataset_sections = re.split(r'\n\*\*\*\n', content)
        
        for section in dataset_sections:
            if not section.strip() or section.startswith('##'):
                continue
                
            dataset = self._extract_dataset_info(section, category_name)
            if dataset and dataset.name:
                self.datasets.append(dataset)
                self.categories_index[category_name].append(dataset)
    
    def _extract_dataset_info(self, section: str, category: str) -> Optional[MedicalDataset]:
        """Extract dataset information from a section of text."""
        lines = section.strip().split('\n')
        if not lines:
            return None
        
        # Extract dataset name (usually the first bold line or first line)
        name_match = re.search(r'__(.+?)__', lines[0])
        name = name_match.group(1) if name_match else lines[0].strip('#').strip()
        
        if not name or len(name) < 3:
            return None
        
        # Extract description (text before URLs)
        description_lines = []
        paper_url = None
        access_url = None
        information_url = None
        data_url = None
        requires_registration = False
        
        for line in lines[1:]:
            line = line.strip()
            
            # Check for registration requirement
            if 'requires registration' in line.lower():
                requires_registration = True
            
            # Extract URLs
            if line.lower().startswith('paper:'):
                paper_url = self._extract_url(line)
            elif line.lower().startswith('access:'):
                access_url = self._extract_url(line)
            elif line.lower().startswith('information:'):
                information_url = self._extract_url(line)
            elif line.lower().startswith('data:'):
                data_url = self._extract_url(line)
            elif line.lower().startswith('overview:'):
                if not information_url:
                    information_url = self._extract_url(line)
            elif line and not line.startswith(('Paper:', 'Access:', 'Information:', 'Data:', 'Overview:')):
                # It's part of the description
                # Remove markdown formatting
                clean_line = re.sub(r'__(.+?)__', r'\1', line)
                if clean_line:
                    description_lines.append(clean_line)
        
        description = ' '.join(description_lines).strip()
        
        return MedicalDataset(
            name=name,
            category=category,
            description=description,
            paper_url=paper_url,
            access_url=access_url,
            information_url=information_url,
            data_url=data_url,
            requires_registration=requires_registration
        )
    
    def _extract_url(self, line: str) -> Optional[str]:
        """Extract URL from a line of text."""
        url_match = re.search(r'https?://[^\s\)]+', line)
        return url_match.group(0) if url_match else None
    
    def browse_by_category(self, category_name: Optional[str] = None) -> List[MedicalDataset]:
        """Browse datasets by category."""
        if category_name:
            return self.categories_index.get(category_name, [])
        return self.datasets
    
    def search_datasets(self, keyword: str, case_sensitive: bool = False) -> List[MedicalDataset]:
        """Search for datasets by keyword in name or description."""
        if not case_sensitive:
            keyword = keyword.lower()
        
        results = []
        for dataset in self.datasets:
            search_text = f"{dataset.name} {dataset.description}"
            if not case_sensitive:
                search_text = search_text.lower()
            
            if keyword in search_text:
                results.append(dataset)
        
        return results
    
    def get_dataset_by_name(self, name: str) -> Optional[MedicalDataset]:
        """Get a specific dataset by exact name match."""
        for dataset in self.datasets:
            if dataset.name.lower() == name.lower():
                return dataset
        return None
    
    def list_categories(self) -> List[Tuple[str, int]]:
        """List all categories with dataset counts."""
        return [(cat, len(datasets)) for cat, datasets in self.categories_index.items()]
    
    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about the datasets."""
        total_datasets = len(self.datasets)
        with_papers = sum(1 for d in self.datasets if d.paper_url)
        with_access = sum(1 for d in self.datasets if d.access_url or d.data_url)
        requires_reg = sum(1 for d in self.datasets if d.requires_registration)
        
        return {
            'total_datasets': total_datasets,
            'datasets_with_papers': with_papers,
            'datasets_with_access': with_access,
            'requires_registration': requires_reg,
            'categories': len(self.categories_index),
            'category_breakdown': {cat: len(datasets) for cat, datasets in self.categories_index.items()}
        }
    
    def display_dataset(self, dataset: MedicalDataset, detailed: bool = True) -> None:
        """Display information about a dataset."""
        print(f"\n{'='*80}")
        print(f"Dataset: {dataset.name}")
        print(f"Category: {dataset.category}")
        print(f"{'='*80}")
        
        if dataset.description:
            print(f"\nDescription:")
            print(f"  {dataset.description}")
        
        if dataset.paper_url:
            print(f"\nPaper: {dataset.paper_url}")
        
        if dataset.access_url:
            print(f"Access: {dataset.access_url}")
        
        if dataset.data_url:
            print(f"Data: {dataset.data_url}")
        
        if dataset.information_url:
            print(f"Information: {dataset.information_url}")
        
        if dataset.requires_registration:
            print(f"\n⚠️  Note: This dataset requires registration")
        
        print(f"{'='*80}\n")
    
    def export_to_json(self, filename: str = "medical_datasets.json") -> None:
        """Export all datasets to a JSON file."""
        data = {
            'categories': list(self.categories_index.keys()),
            'total_datasets': len(self.datasets),
            'datasets': [asdict(d) for d in self.datasets]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(self.datasets)} datasets to {filename}")
    
    def interactive_browse(self) -> None:
        """Start an interactive browsing session."""
        print("\n" + "="*80)
        print("Medical Data Browser - Interactive Mode")
        print("="*80)
        
        while True:
            print("\nOptions:")
            print("1. Browse by category")
            print("2. Search datasets")
            print("3. View statistics")
            print("4. List all categories")
            print("5. Export to JSON")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self._browse_category_interactive()
            elif choice == '2':
                self._search_interactive()
            elif choice == '3':
                self._display_statistics()
            elif choice == '4':
                self._list_categories_interactive()
            elif choice == '5':
                self.export_to_json()
            elif choice == '6':
                print("Thank you for using Medical Data Browser!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _browse_category_interactive(self) -> None:
        """Interactive category browsing."""
        categories = list(self.categories_index.keys())
        
        print("\nAvailable Categories:")
        for idx, cat in enumerate(categories, 1):
            count = len(self.categories_index[cat])
            print(f"{idx}. {cat} ({count} datasets)")
        
        try:
            choice = int(input("\nEnter category number (0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(categories):
                category = categories[choice - 1]
                datasets = self.browse_by_category(category)
                
                print(f"\nDatasets in '{category}':")
                for idx, dataset in enumerate(datasets, 1):
                    print(f"{idx}. {dataset.name}")
                
                dataset_choice = int(input(f"\nEnter dataset number to view details (0 to cancel): "))
                if 0 < dataset_choice <= len(datasets):
                    self.display_dataset(datasets[dataset_choice - 1])
        except (ValueError, IndexError):
            print("Invalid input.")
    
    def _search_interactive(self) -> None:
        """Interactive search."""
        keyword = input("\nEnter search keyword: ").strip()
        if not keyword:
            return
        
        results = self.search_datasets(keyword)
        
        if not results:
            print(f"No datasets found matching '{keyword}'")
            return
        
        print(f"\nFound {len(results)} dataset(s) matching '{keyword}':")
        for idx, dataset in enumerate(results, 1):
            print(f"{idx}. {dataset.name} ({dataset.category})")
        
        try:
            choice = int(input(f"\nEnter dataset number to view details (0 to cancel): "))
            if 0 < choice <= len(results):
                self.display_dataset(results[choice - 1])
        except ValueError:
            print("Invalid input.")
    
    def _display_statistics(self) -> None:
        """Display statistics about the datasets."""
        stats = self.get_statistics()
        
        print("\n" + "="*80)
        print("Dataset Statistics")
        print("="*80)
        print(f"Total Datasets: {stats['total_datasets']}")
        print(f"Datasets with Papers: {stats['datasets_with_papers']}")
        print(f"Datasets with Access Links: {stats['datasets_with_access']}")
        print(f"Datasets Requiring Registration: {stats['requires_registration']}")
        print(f"Total Categories: {stats['categories']}")
        
        print("\nDatasets by Category:")
        for cat, count in stats['category_breakdown'].items():
            print(f"  - {cat}: {count}")
        print("="*80)
    
    def _list_categories_interactive(self) -> None:
        """List all categories with counts."""
        categories = self.list_categories()
        
        print("\n" + "="*80)
        print("Categories")
        print("="*80)
        for cat, count in categories:
            print(f"{cat}: {count} datasets")
        print("="*80)


def main():
    """Main function to run the Medical Data Browser."""
    parser = argparse.ArgumentParser(
        description='Browse and search medical datasets from README.md',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--readme',
        default='README.md',
        help='Path to README.md file (default: README.md)'
    )
    
    parser.add_argument(
        '--category',
        help='Browse datasets by category name'
    )
    
    parser.add_argument(
        '--search',
        help='Search datasets by keyword'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Display statistics about datasets'
    )
    
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export datasets to JSON file'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Start interactive browsing mode'
    )
    
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List all available categories'
    )
    
    args = parser.parse_args()
    
    # Initialize browser