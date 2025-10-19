"""Export functionality for mindlite."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

from .db import get_conn, list_items


def export_json(conn, path: str) -> None:
    """Export all items to JSON file."""
    items = list_items(conn)
    
    # Convert to serializable format
    export_data = []
    for item in items:
        export_item = dict(item)
        # Convert any non-serializable fields if needed
        export_data.append(export_item)
    
    output_path = Path(path)
    output_path.write_text(json.dumps(export_data, indent=2), encoding="utf-8")


def export_md(conn, path: str) -> None:
    """Export all items to Markdown file."""
    items = list_items(conn)
    
    lines = ["# Mindlite Export\n"]
    
    for item in items:
        lines.append(f"## #{item['id']} {item['title']}")
        lines.append(f"- Type: {item['type']}")
        lines.append(f"- Status: {item['status']}")
        lines.append(f"- Priority: {item['priority']}")
        lines.append(f"- Due: {item['due_date'] or 'Not set'}")
        lines.append(f"- Tags: {', '.join(item['tags']) if item['tags'] else 'None'}")
        lines.append(f"- Created: {item['created_at']}")
        lines.append(f"- Updated: {item['updated_at']}")
        
        if item['body']:
            lines.append("\n" + item['body'])
        else:
            lines.append("\nNo body text.")
        
        lines.append("\n---\n")
    
    output_path = Path(path)
    output_path.write_text("\n".join(lines), encoding="utf-8")
