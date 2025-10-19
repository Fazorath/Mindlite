from __future__ import annotations

from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from .screens import MainScreen


STATE_FILE = Path.home() / ".matrix_mind_ui.json"


class MatrixMindApp(App):
    CSS_PATH = "themes/matrix.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Container(id="root")
        yield Footer()

    def on_mount(self) -> None:
        self.push_screen(MainScreen())


def run() -> None:
    app = MatrixMindApp()
    app.run()


if __name__ == "__main__":
    run()


