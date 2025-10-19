from __future__ import annotations

from textual.containers import Horizontal, Vertical
from textual.widgets import Static


class Column(Vertical):
    def __init__(self, title: str, *children, **kwargs):
        super().__init__(*children, **kwargs)
        self.title = title

    def compose(self):
        yield Static(f"[bold]{self.title}")

    def _clear_column_safe(self) -> None:
        """Clear column content safely across Textual versions."""
        try:
            # Remove all children except the title
            children_to_remove = [child for child in self.children if child != self.query_one(Static)]
            for child in children_to_remove:
                child.remove()
        except Exception:
            # Fallback: rebuild the column
            self.remove_children()
            self.mount(Static(f"[bold]{self.title}"))


class BoardViewWidget(Horizontal):
    def compose(self):
        self.todo = Column("TODO", id="col-todo")
        self.doing = Column("DOING", id="col-doing")
        self.blocked = Column("BLOCKED", id="col-blocked")
        self.done = Column("DONE", id="col-done")
        yield self.todo
        yield self.doing
        yield self.blocked
        yield self.done

    def set_rows(self, rows) -> None:
        # Clear columns safely
        for col in [self.todo, self.doing, self.blocked, self.done]:
            col._clear_column_safe()
        
        # Group by status
        by_status = {"todo": [], "doing": [], "blocked": [], "done": []}
        for r in rows:
            by_status[r["status"]].append(r)
        
        # Populate columns
        for status, col in [
            ("todo", self.todo),
            ("doing", self.doing),
            ("blocked", self.blocked),
            ("done", self.done),
        ]:
            for r in by_status[status]:
                col.mount(Static(f"[bold]{r['id']}[/] {r['title']} [dim]({r['tags']})[/]"))


