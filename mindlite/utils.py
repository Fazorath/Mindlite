"""Utility functions for mindlite."""

from __future__ import annotations

import sys
from typing import List, Optional, Tuple


def comma_split(s: Optional[str]) -> List[str]:
    """Split comma-separated string into list of trimmed strings."""
    if not s:
        return []
    return [item.strip() for item in s.split(",") if item.strip()]


def confirm(prompt: str) -> bool:
    """Ask user for yes/no confirmation."""
    while True:
        response = input(f"{prompt} [y/N]: ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no", ""):
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def print_table(rows: List[dict], columns: List[Tuple[str, str]]) -> None:
    """
    Print a simple ASCII table with dynamic column widths.
    
    Args:
        rows: List of dictionaries representing table rows
        columns: List of (field_name, display_name) tuples
    """
    if not rows:
        print("No items found.")
        return
    
    # Get terminal width for better column sizing
    import shutil
    terminal_width = shutil.get_terminal_size().columns
    
    # Calculate column widths more intelligently
    widths = {}
    for field_name, display_name in columns:
        # Start with header width
        widths[field_name] = len(display_name)
    
    # Calculate content widths
    for row in rows:
        for field_name, _ in columns:
            value = str(row.get(field_name, ""))
            # Don't truncate during width calculation
            widths[field_name] = max(widths[field_name], len(value))
    
    # Distribute available width proportionally
    total_content_width = sum(widths.values())
    available_width = terminal_width - (len(columns) - 1) * 3  # Account for separators
    
    if total_content_width > available_width:
        # Scale down proportionally, but keep minimum widths
        scale_factor = available_width / total_content_width
        for field_name in widths:
            new_width = max(8, int(widths[field_name] * scale_factor))
            widths[field_name] = min(new_width, widths[field_name])  # Don't make wider than content
    
    # Print header
    header_parts = []
    separator_parts = []
    for field_name, display_name in columns:
        width = widths[field_name]
        header_parts.append(display_name.ljust(width))
        separator_parts.append("-" * width)
    
    print(" | ".join(header_parts))
    print("-+-".join(separator_parts))
    
    # Print rows
    for row in rows:
        row_parts = []
        for field_name, _ in columns:
            value = str(row.get(field_name, ""))
            width = widths[field_name]
            # Truncate with ellipsis if needed
            if len(value) > width:
                value = value[:width-3] + "..."
            row_parts.append(value.ljust(width))
        print(" | ".join(row_parts))


def print_item_detail(item: dict) -> None:
    """Print detailed view of a single item."""
    print(f"#{item['id']} {item['title']}")
    print("=" * (len(str(item['id'])) + len(item['title']) + 2))
    print(f"Type: {item['type']}")
    print(f"Status: {item['status']}")
    print(f"Priority: {item['priority']}")
    print(f"Due: {item['due_date'] or 'Not set'}")
    print(f"Tags: {', '.join(item['tags']) if item['tags'] else 'None'}")
    print(f"Created: {item['created_at']}")
    print(f"Updated: {item['updated_at']}")
    if item['body']:
        print("\nBody:")
        print(item['body'])
    else:
        print("\nNo body text.")


def error_exit(message: str, code: int = 1) -> None:
    """Print error message and exit with code."""
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)
