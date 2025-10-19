from __future__ import annotations

from textual.widgets import Static


class MatrixFooter(Static):
    def on_mount(self) -> None:
        self.update("[dim]A: Add  E: Edit  Space: Cycle  V: Toggle View  Q: Quit[/]")


