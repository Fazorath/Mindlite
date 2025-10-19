from __future__ import annotations

from textual.widgets import Static


class MatrixHeader(Static):
    def on_mount(self) -> None:
        self.update("[bold #00E676]MATRIX MIND[/]")


