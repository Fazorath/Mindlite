from __future__ import annotations

import random
from typing import List

from textual.reactive import reactive
from textual.widget import Widget


class MatrixRain(Widget):
    """Low-intensity background matrix rain."""

    frame = reactive(0)

    def on_mount(self) -> None:
        self.set_interval(0.12, self.tick)

    def tick(self) -> None:
        self.frame += 1
        self.refresh()

    def render(self):
        width = max(1, self.size.width)
        height = max(1, self.size.height)
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lines: List[str] = []
        rng = random.Random(self.frame)
        for _ in range(height):
            row = []
            for _ in range(width):
                ch = rng.choice(chars)
                if rng.random() < 0.92:
                    ch = " "
                row.append(f"[dim #00BFA5]{ch}[/]")
            lines.append("".join(row))
        return "\n".join(lines)


