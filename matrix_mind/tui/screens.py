from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Horizontal
from textual.widgets import Static
from textual import events

from .. import db

from .widgets.header import MatrixHeader
from .widgets.footer import MatrixFooter
from .widgets.sidebar import Sidebar
from .widgets.list_view import ListViewWidget
from .widgets.board_view import BoardViewWidget
from .widgets.detail_panel import DetailPanel
from .widgets.matrix_rain import MatrixRain


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield MatrixHeader()
        with Container(id="body"):
            yield MatrixRain(id="rain")
            with Horizontal(id="content"):
                yield Sidebar(id="sidebar")
                yield ListViewWidget(id="main-list")
                yield BoardViewWidget(id="main-board")
                yield DetailPanel(id="detail")
        yield MatrixFooter()

    def on_mount(self) -> None:
        rows = db.list_items()
        listw = self.query_one("#main-list", ListViewWidget)
        listw.set_rows(rows)
        board = self.query_one("#main-board", BoardViewWidget)
        board.set_rows(rows)
        board.display = False

    async def on_key(self, event: events.Key) -> None:
        if event.key.lower() == "v":
            listw = self.query_one("#main-list", ListViewWidget)
            board = self.query_one("#main-board", BoardViewWidget)
            show_board = not board.display
            board.display = show_board
            listw.display = not show_board
        elif event.key.lower() == "r":
            rows = db.list_items()
            self.query_one("#main-list", ListViewWidget).set_rows(rows)
            self.query_one("#main-board", BoardViewWidget).set_rows(rows)
        elif event.key == " ":
            listw = self.query_one("#main-list", ListViewWidget)
            if listw.display:
                if listw.cursor_row is not None:
                    row_key = listw.get_row_at(listw.cursor_row).key
                    if isinstance(row_key, int):
                        self._cycle_status(row_key)
                        rows = db.list_items()
                        listw.set_rows(rows)
                        self.query_one("#main-board", BoardViewWidget).set_rows(rows)

    def _cycle_status(self, item_id: int) -> None:
        row = db.get_item(item_id)
        if not row:
            return
        order = ["todo", "doing", "blocked", "done"]
        try:
            idx = order.index(row["status"])  # type: ignore[index]
        except ValueError:
            idx = 0
        next_status = order[(idx + 1) % len(order)]
        db.set_status(item_id, next_status)  # type: ignore[arg-type]


