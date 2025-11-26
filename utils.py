"""
Utility functions for the Medical Data Browser.

This module provides helper functions for parsing, processing, and formatting
medical dataset information from markdown content.
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import json
from datetime import datetime


# Regular expression patterns for parsing
URL_PATTERN = re.compile(r'https?://[^\s\)]+')
BOLD_TEXT_PATTERN = re.compile(r'__(.+?)__')
CATEGORY_HEADER_PATTERN = re.compile(r'##\s+(\d+)\.\s+(.+)')
MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')


def extract_urls_from_text(text: str) -> List[str]:
    """
    Extract all URLs from a given text.
    
    Args:
        text: String containing potential URLs
        
    Returns:
        List of URLs found in the text
        
    Example:
        >>> extract_urls_from_text("Visit https://example.com and http://test.org")
        ['https://example.com', 'http://test.org']
    """
    return URL_PATTERN.findall(text)


def extract_url_from_line(line: str, prefix: Optional[str] = None) -> Optional[str]:
    """
    Extract URL from a line, optionally checking for a specific prefix.
    
    Args:
        line: Text line potentially containing a URL
        prefix: Optional prefix to check (e.g., "Access:", "Paper:")
        
    Returns:
        Extracted URL or None if not found
        
    Example:
        >>> extract_url_from_line("Access: https://example.com/data")
        'https://example.com/data'
    """
    if prefix and not line.lower().startswith(prefix.lower()):
        return None
    
    urls = extract_urls_from_text(line)
    return urls[0] if urls else None


def clean_markdown_formatting(text: str) -> str:
    """
    Remove markdown formatting from text.
    
    Args:
        text: String with markdown formatting
        
    Returns:
        Clean text without markdown syntax
        
    Example:
        >>> clean_markdown_formatting("This is __bold__ and *italic* text")
        'This is bold and italic text'
    """
    # Remove bold formatting
    text = BOLD_TEXT_PATTERN.sub(r'\1', text)
    
    # Remove italic formatting
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Remove code formatting
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Convert markdown links to just text
    text = MARKDOWN_LINK_PATTERN.sub(r'\1', text)
    
    return text.strip()


def parse_category_header(line: str) -> Optional[Tuple[str, str]]:
    """
    Parse a category header line.
    
    Args:
        line: Category header line from markdown
        
    Returns:
        Tuple of (category_number, category_name) or None if not a category header
        
    Example:
        >>> parse_category_header("## 1. Medical Imaging Data")
        ('1', 'Medical Imaging Data')
    """
    match = CATEGORY_HEADER_PATTERN.match(line.strip())
    if match:
        return match.group(1), match.group(2).strip()
    return None


def extract_dataset_name(text: str) -> Optional[str]:
    """
    Extract dataset name from text, handling both bold and plain formats.
    
    Args:
        text: Text potentially containing dataset name
        
    Returns:
        Extracted dataset name or None
        
    Example:
        >>> extract_dataset_name("__EchoNet-Dynamic__")
        'EchoNet-Dynamic'
    """
    # Try to extract from bold formatting
    match = BOLD_TEXT_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    
    # Otherwise, use the first line cleaned of markdown
    name = clean_markdown_formatting(text.split('\n')[0])
    name = name.strip('#').strip()
    
    return name if len(name) >= 3 else None


def check_registration_required(text: str) -> bool:
    """
    Check if text indicates registration is required.
    
    Args:
        text: Text to check for registration requirements
        
    Returns:
        True if registration is required, False otherwise
        
    Example:
        >>> check_registration_required("Access requires registration")
        True
    """
    keywords = [
        'requires registration',
        'registration required',
        'sign up required',
        'account required'
    ]
    
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def split_by_delimiter(content: str, delimiter: str = '\n***\n') -> List[str]:
    """
    Split content by a delimiter, filtering empty sections.
    
    Args:
        content: Text content to split
        delimiter: Delimiter string to split by
        
    Returns:
        List of non-empty content sections
        
    Example:
        >>> split_by_delimiter("Section 1\\n***\\nSection 2")
        ['Section 1', 'Section 2']
    """
    sections = content.split(delimiter)
    return [s.strip() for s in sections if s.strip()]


def extract_metadata_from_section(section: str) -> Dict[str, Any]:
    """
    Extract metadata fields from a dataset section.
    
    Args:
        section: Text section containing dataset information
        
    Returns:
        Dictionary with extracted metadata fields
        
    Example:
        >>> text = "Paper: https://example.com\\nAccess: https://data.com"
        >>> extract_metadata_from_section(text)
        {'paper_url': 'https://example.com', 'access_url': 'https://data.com'}
    """
    metadata = {
        'paper_url': None,
        'access_url': None,
        'information_url': None,
        'data_url': None,
        'overview_url': None,
        'requires_registration': False
    }
    
    lines = section.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
        
        # Check for registration requirement
        if check_registration_required(line):
            metadata['requires_registration'] = True
        
        # Extract URLs by prefix
        if line.lower().startswith('paper:'):
            metadata['paper_url'] = extract_url_from_line(line)
        elif line.lower().startswith('access:'):
            metadata['access_url'] = extract_url_from_line(line)
        elif line.lower().startswith('information:'):
            metadata['information_url'] = extract_url_from_line(line)
        elif line.lower().startswith('data:'):
            metadata['data_url'] = extract_url_from_line(line)
        elif line.lower().startswith('overview:'):
            metadata['overview_url'] = extract_url_from_line(line)
    
    return metadata


def extract_description_lines(section: str, skip_prefixes: Optional[List[str]] = None) -> List[str]:
    """
    Extract description lines from a section, skipping lines with specific prefixes.
    
    Args:
        section: Text section to process
        skip_prefixes: List of prefixes to skip (default: common metadata prefixes)
        
    Returns:
        List of cleaned description lines
    """
    if skip_prefixes is None:
        skip_prefixes = [
            'paper:', 'access:', 'information:', 'data:', 
            'overview:', 'link:', 'website:', 'embeddings:',
            'code:', 'interactive tool:'
        ]
    
    lines = section.split('\n')
    description_lines = []
    
    for line in lines[1:]:  # Skip first line (usually the name)
        line = line.strip()
        
        if not line or line.startswith('##'):
            continue
        
        # Check if line starts with any skip prefix
        if any(line.lower().startswith(prefix) for prefix in skip_prefixes):
            continue
        
        # Clean and add the line
        clean_line = clean_markdown_formatting(line)
        if clean_line:
            description_lines.append(clean_line)
    
    return description_lines


def format_dataset_output(dataset_dict: Dict[str, Any], format_type: str = 'text') -> str:
    """
    Format dataset information for output.
    
    Args:
        dataset_dict: Dictionary containing dataset information
        format_type: Output format ('text', 'markdown', or 'json')
        
    Returns:
        Formatted string representation of the dataset
    """
    if format_type == 'json':
        return json.dumps(dataset_dict, indent=2, ensure_ascii=False)
    
    elif format_type == 'markdown':
        output = [f"## {dataset_dict.get('name', 'Unknown Dataset')}"]
        output.append(f"\n**Category:** {dataset_dict.get('category', 'N/A')}")
        
        if dataset_dict.get('description'):
            output.append(f"\n**Description:** {dataset_dict['description']}")
        
        if dataset_dict.get('paper_url'):
            output.append(f"\n**Paper:** {dataset_dict['paper_url']}")
        
        if dataset_dict.get('access_url'):
            output.append(f"\n**Access:** {dataset_dict['access_url']}")
        
        if dataset_dict.get('data_url'):
            output.append(f"\n**Data:** {dataset_dict['data_url']}")
        
        if dataset_dict.get('requires_registration'):
            output.append("\n**Note:** This dataset requires registration")
        
        return '\n'.join(output)
    
    else:  # text format
        output = []
        output.append(f"Dataset: {dataset_dict.get('name', 'Unknown')}")
        output.append(f"Category: {dataset_dict.get('category', 'N/A')}")
        
        if dataset_dict.get('description'):
            output.append(f"Description: {dataset_dict['description']}")
        
        if dataset_dict.get('paper_url'):
            output.append(f"Paper: {dataset_dict['paper_url']}")
        
        if dataset_dict.get('access_url'):
            output.append(f"Access: {dataset_dict['access_url']}")
        
        return '\n'.join(output)


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length of output
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
        
    Example:
        >>> truncate_text("This is a very long text", max_length=10)
        'This is...'
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)].strip() + suffix


def normalize_category_name(category: str) -> str:
    """
    Normalize category name for consistent comparison and storage.
    
    Args:
        category: Category name to normalize
        
    Returns:
        Normalized category name
        
    Example:
        >>> normalize_category_name("  Medical Imaging Data  ")
        'medical_imaging_data'
    """
    # Convert to lowercase
    normalized = category.lower()
    
    # Replace spaces and special characters with underscores
    normalized = re.sub(r'[^\w]+', '_', normalized)
    
    # Remove leading/trailing underscores
    normalized = normalized.strip('_')
    
    return normalized


def validate_url(url: str) -> bool:
    """
    Validate if a string is a properly formatted URL.
    
    Args:
        url: String to validate
        
    Returns:
        True if valid URL, False otherwise
        
    Example:
        >>> validate_url("https://example.com")
        True
        >>> validate_url("not a url")
        False
    """
    if not url:
        return False
    
    url_regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_regex.match(url))


def count_words(text: str) -> int:
    """
    Count the number of words in a text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words
        
    Example:
        >>> count_words("This is a test")
        4
    """
    if not text:
        return 0
    
    # Split by whitespace and filter empty strings
    words = [w for w in text.split() if w]
    return len(words)


def create_summary_statistics(datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create summary statistics for a list of datasets.
    
    Args:
        datasets: List of dataset dictionaries
        
    Returns:
        Dictionary containing summary statistics
    """
    if not datasets:
        return {
            'total_datasets': 0,
            'with_papers': 0,
            'with_access': 0,
            'requires_registration': 0,
            'average_description_length': 0
        }
    
    stats = {
        'total_datasets': len(datasets),
        'with_papers': sum(1 for d in datasets if d.get('paper_url')),
        'with_access': sum(1 for d in datasets if d.get('access_url') or d.get('data_url')),
        'requires_registration': sum(1 for d in datasets if d.get('requires_registration')),
        'categories': {}
    }
    
    # Calculate average description length
    desc_lengths = [len(d.get('description', '')) for d in datasets if d.get('description')]
    stats['average_description_length'] = sum(desc_lengths) / len(desc_lengths) if desc_lengths else 0
    
    # Count by category
    for dataset in datasets:
        category = dataset.get('category', 'Unknown')
        stats['categories'][category] = stats['categories'].get(category, 0) + 1
    
    return stats


def filter_datasets(
    datasets: List[Dict[str, Any]], 
    category: Optional[str] = None,
    has_paper: Optional[bool] = None,
    has_access: Optional[bool] = None,
    registration_required: Optional[bool] = None,
    keyword: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter datasets based on various criteria.
    
    Args:
        datasets: List of dataset dictionaries to filter
        category: Filter by category name
        has_paper: Filter by presence of paper URL
        has_access: Filter by presence of access URL
        registration_required: Filter by registration requirement
        keyword: Filter by keyword in name or description
        
    Returns:
        Filtered list of