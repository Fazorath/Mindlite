from __future__ import annotations

from .models import Item
from . import db


def seed() -> None:
    samples = [
        Item(id=None, type="todo", title="Wire up CLI with Typer", priority="high", tags=["cli", "milestone"]),
        Item(id=None, type="idea", title="Matrix rain widget", priority="med", tags=["tui", "fx"], body="Gentle background rain"),
        Item(id=None, type="issue", title="Status cycling bug", priority="med", tags=["bug"], body="Space should cycle statuses"),
        Item(id=None, type="todo", title="Kanban board view", priority="high", tags=["tui", "board"], body="Columns: TODO/DOING/BLOCKED/DONE"),
    ]
    for it in samples:
        db.add_item(it)


if __name__ == "__main__":
    db.init_db()
    seed()
    print("Seeded sample data.")


