from __future__ import annotations
from typing import Iterable, Mapping, Any

from textual.widgets import DataTable

class ListViewWidget(DataTable):
    """Main list view for items (ID, Type, Title, Status, Priority, Due, Tags)."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._columns_ready = False
        # Visual tweaks for the Matrix vibe; theme colors are in TCSS.
        self.zebra_stripes = True
        self.cursor_type = "row"

    def _ensure_columns(self) -> None:
        if not self._columns_ready:
            self.clear()  # full clear once
            self.add_columns("ID", "Type", "Title", "Status", "Priority", "Due", "Tags")
            self._columns_ready = True

    def _clear_rows_safe(self) -> None:
        """
        Clear just the rows in a way that's compatible across Textual versions.
        Some versions support clear(rows=True); others only have clear().
        """
        try:
            # Newer API variant (if available in your env)
            super().clear(rows=True)  # type: ignore[arg-type]
        except TypeError:
            # Fallback: manually remove rows
            try:
                # DataTable provides row_count; remove from 0 repeatedly
                while self.row_count > 0:
                    self.remove_row(0)
            except Exception:
                # Last resort: full clear and re-add columns
                self.clear()
                self._columns_ready = False
                self._ensure_columns()

    def set_rows(self, rows: Iterable[Mapping[str, Any]]) -> None:
        """Populate rows from an iterable of sqlite3.Row or dicts."""
        self._ensure_columns()
        self._clear_rows_safe()
        for r in rows:
            # sqlite3.Row supports dict-style access
            self.add_row(
                str(r["id"]),
                r["type"],
                r["title"],
                r["status"],
                r["priority"],
                r["due_date"] or "",
                ", ".join(r.get("tags", [])) if isinstance(r, dict) else "",
            )
        # Keep the first row selected for keyboard nav UX
        if self.row_count:
            self.cursor_coordinate = (0, 0)


