from __future__ import annotations

from textual.widgets import Static


class DetailPanel(Static):
    def on_mount(self) -> None:
        self.update("[dim]Select an item to view details[/]")


