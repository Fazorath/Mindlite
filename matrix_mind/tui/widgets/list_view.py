from __future__ import annotations

from textual.widgets import DataTable


STATUS_COLOR = {
    "todo": "#00BFA5",
    "doing": "#00E676",
    "blocked": "red3",
    "done": "gray62",
}


class ListViewWidget(DataTable):
    def on_mount(self) -> None:
        self.add_columns("ID", "Type", "Title", "Status", "Priority", "Due", "Tags")

    def set_rows(self, rows) -> None:
        self.clear(rows=True)
        for r in rows:
            self.add_row(
                str(r["id"]),
                r["type"],
                r["title"],
                f"[{STATUS_COLOR.get(r['status'],'white')}]" + r["status"] + "[/]",
                r["priority"],
                r["due_date"] or "",
                r["tags"],
                key=r["id"],
            )


