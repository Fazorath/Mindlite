"""Data models and validation for mindlite."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

# Type aliases
ItemType = Literal["todo", "idea", "issue"]
ItemStatus = Literal["todo", "doing", "blocked", "done"]
Priority = Literal["low", "med", "high"]


def now_iso() -> str:
    """Get current UTC timestamp as ISO string."""
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def parse_date(s: Optional[str]) -> Optional[str]:
    """
    Parse date string in YYYY-MM-DD format.
    
    Args:
        s: Date string or None
        
    Returns:
        Validated date string or None
        
    Raises:
        ValueError: If date format is invalid
    """
    if not s:
        return None
    
    # Basic format validation
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        raise ValueError(f"Invalid date format: {s}. Use YYYY-MM-DD")
    
    # Try to parse to validate it's a real date
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError as e:
        raise ValueError(f"Invalid date: {s}. {e}")


def validate_type(item_type: str) -> ItemType:
    """Validate item type."""
    if item_type not in ("todo", "idea", "issue"):
        raise ValueError(f"Invalid type: {item_type}. Must be one of: todo, idea, issue")
    return item_type


def validate_status(status: str) -> ItemStatus:
    """Validate item status."""
    if status not in ("todo", "doing", "blocked", "done"):
        raise ValueError(f"Invalid status: {status}. Must be one of: todo, doing, blocked, done")
    return status


def validate_priority(priority: str) -> Priority:
    """Validate priority level."""
    if priority not in ("low", "med", "high"):
        raise ValueError(f"Invalid priority: {priority}. Must be one of: low, med, high")
    return priority


@dataclass
class Item:
    """Represents a mindlite item."""
    
    id: Optional[int]
    type: ItemType
    title: str
    body: str = ""
    status: ItemStatus = "todo"
    priority: Priority = "med"
    due_date: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    tags: list[str] = None
    
    def __post_init__(self):
        """Initialize default values after dataclass creation."""
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = now_iso()
        if not self.updated_at:
            self.updated_at = now_iso()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database operations."""
        return {
            "type": self.type,
            "title": self.title,
            "body": self.body,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
