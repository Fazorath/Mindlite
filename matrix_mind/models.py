from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Literal, Optional, Sequence, List, Dict, Any

ItemType = Literal["todo", "idea", "issue"]
ItemStatus = Literal["todo", "doing", "blocked", "done"]
Priority = Literal["low", "med", "high"]


def utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


@dataclass(slots=True)
class Item:
    id: Optional[int]
    type: ItemType
    title: str
    body: str = ""
    status: ItemStatus = "todo"
    priority: Priority = "med"
    due_date: Optional[str] = None  # ISO date (YYYY-MM-DD)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    tags: List[str] = field(default_factory=list)

    def to_row(self) -> Dict[str, Any]:
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


