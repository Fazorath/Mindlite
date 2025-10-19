from __future__ import annotations

from textual.containers import Vertical
from textual.widgets import Static


class Sidebar(Vertical):
    def compose(self):
        yield Static("[bold]Filters[/]")
        yield Static("All | Todos | Ideas | Issues")
        yield Static("[dim]Open Only  Due Soon[/]")


