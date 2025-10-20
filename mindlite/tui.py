"""
Curses UI for mindlite — stdlib-only.
Layout:
  ┌ Sidebar (nav) ┐ ┌──────────────────────── Reader ────────────────────────┐
  │ > Item A      │ │ [#12] Format-Resume (todo • high • due 2025-10-25)     │
  │   Item B      │ │ -----------------------------------------------------   │
  │   Item C      │ │ Wrapped body text...                                    │
  │   …           │ │                                                         │
  └───────────────┘ └────────────────────────────────────────────────────────┘
"""

from __future__ import annotations
import curses
import textwrap
import time
from typing import List, Tuple
from . import db

MIN_W = 68
SIDEBAR_MIN = 24
PADDING = 1


def _safe_color_init():
    """Initialize color pairs safely."""
    curses.start_color()
    if curses.has_colors():
        curses.use_default_colors()
        # 1: sidebar normal, 2: selection, 3: right border/title
        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(3, curses.COLOR_CYAN, -1)


def _draw_sidebar(win, items, idx, top):
    """Draw the sidebar with item list."""
    h, w = win.getmaxyx()
    win.erase()
    win.box()  # thin box like epr TOC
    max_rows = h - 2
    visible = items[top: top + max_rows]
    for i, it in enumerate(visible):
        y = i + 1
        prefix = "> " if (top + i) == idx else "  "
        title = it["title"]
        line = (prefix + title)[: w - 2]
        if (top + i) == idx:
            try:
                win.addstr(y, 1, line.ljust(w-2), curses.color_pair(2))
            except curses.error:
                pass
        else:
            try:
                win.addstr(y, 1, line.ljust(w-2), curses.color_pair(1))
            except curses.error:
                pass
    win.noutrefresh()


def _wrap(text, width):
    """Wrap text to specified width."""
    wrapper = textwrap.TextWrapper(width=width, drop_whitespace=True, replace_whitespace=False)
    lines = []
    for para in (text or "").splitlines() or [""]:
        lines.extend(wrapper.wrap(para) if para.strip() else [""])
    return lines


def _draw_reader(win, item, scroll):
    """Draw the reader pane with item details."""
    h, w = win.getmaxyx()
    win.erase()
    # Border in cyan if available
    try:
        win.attron(curses.color_pair(3))
        win.box()
        win.attroff(curses.color_pair(3))
    except curses.error:
        win.box()

    inner_w = max(1, w - 2 - PADDING*2)
    x0 = 1 + PADDING
    y0 = 1 + PADDING

    # Title bar
    title = f"[#{item['id']}] {item['title']}"
    meta = f"{item['type']} • {item['status']} • {item['priority']}" + (f" • due {item['due_date']}" if item['due_date'] else "")
    title_line = (title[:inner_w]).ljust(inner_w)
    meta_line  = (meta[:inner_w]).ljust(inner_w)

    try:
        win.addstr(y0, x0, title_line, curses.A_BOLD)
        win.addstr(y0+1, x0, meta_line)
    except curses.error:
        pass

    # Separator
    sep_y = y0 + 2
    try:
        win.hline(sep_y, x0, curses.ACS_HLINE, inner_w)
    except curses.error:
        pass

    # Body
    body_lines = _wrap(item.get("body",""), inner_w)
    # Available body rows
    start_y = sep_y + 1
    avail = (h - 2) - (start_y)
    page = body_lines[scroll: scroll + max(0, avail)]
    for i, line in enumerate(page):
        if start_y + i >= h - 1:
            break
        try:
            win.addstr(start_y + i, x0, line.ljust(inner_w))
        except curses.error:
            pass

    # Scrollbar hint (optional)
    if len(body_lines) > avail:
        pct = int((min(len(body_lines)-1, scroll) / max(1, len(body_lines)-avail)) * 100)
        hint = f"{pct:3d}%"
        try:
            win.addstr(h-2, w-len(hint)-2, hint, curses.A_DIM)
        except curses.error:
            pass

    win.noutrefresh()


def _fetch_items():
    """Fetch items from database."""
    # minimal list: id, title, meta; sorted by updated_at desc
    conn = db.ensure_db()
    try:
        rows = db.list_items(conn, {"open_only": False})
        # Ensure dict-like
        return [dict(r) for r in rows]
    finally:
        conn.close()


def run(stdscr):
    """Main curses application loop."""
    curses.curs_set(0)
    _safe_color_init()
    stdscr.nodelay(False)
    stdscr.keypad(True)

    # layout
    items = _fetch_items()
    if not items:
        items = [{"id":0,"type":"todo","status":"todo","priority":"med","due_date":"","title":"(no items yet)","body":"Use: python -m mindlite add \"Title\" --type todo"}]

    idx = 0
    top = 0             # sidebar scroll
    scroll = 0          # reader scroll

    while True:
        stdscr.erase()
        H, W = stdscr.getmaxyx()
        if W < MIN_W:
            msg = "Enlarge terminal (min width ~68)"
            stdscr.addstr(0, 0, msg)
            stdscr.refresh()
            ch = stdscr.getch()
            if ch in (ord('q'), 27):
                break
            continue

        sidebar_w = max(SIDEBAR_MIN, int(W * 0.33))
        reader_w  = W - sidebar_w - 1
        sidebar_h = H - 1
        reader_h  = H - 1

        sidebar = curses.newwin(sidebar_h, sidebar_w, 0, 0)
        reader  = curses.newwin(reader_h,  reader_w,  0, sidebar_w + 1)

        # keep selection and scroll in bounds
        idx = max(0, min(idx, len(items)-1))
        if idx < top: top = idx
        if idx >= top + (sidebar_h - 2): top = idx - (sidebar_h - 3)
        scroll = max(0, scroll)

        _draw_sidebar(sidebar, items, idx, top)
        _draw_reader(reader, items[idx], scroll)
        curses.doupdate()

        ch = stdscr.getch()

        if ch in (ord('q'), 27):  # q or ESC
            break
        elif ch in (curses.KEY_UP, ord('k')):
            idx = max(0, idx - 1); scroll = 0
        elif ch in (curses.KEY_DOWN, ord('j')):
            idx = min(len(items)-1, idx + 1); scroll = 0
        elif ch in (curses.KEY_NPAGE, ord(' ')):  # page down body
            scroll += reader_h // 2
        elif ch in (curses.KEY_PPAGE, ):
            scroll = max(0, scroll - reader_h // 2)
        elif ch in (ord('g'), ):
            scroll = 0
        elif ch in (ord('G'), ):
            # jump near bottom of body
            # (lazy approach; actual height computed in draw)
            scroll += 10_000
        elif ch in (ord('r'), ):
            # refresh data from DB
            items = _fetch_items()
            idx = min(idx, len(items)-1)
            scroll = 0
        elif ch == curses.KEY_RESIZE:
            # redraw loop will handle it
            pass
        # Simple status cycle shortcut: s
        elif ch in (ord('s'), ):
            # rotate status todo->doing->blocked->done->todo
            order = ("todo","doing","blocked","done")
            cur = items[idx]["status"]
            nxt = order[(order.index(cur) + 1) % len(order)]
            conn = db.ensure_db()
            try:
                conn.execute("UPDATE items SET status=?, updated_at=datetime('now') WHERE id=?", (nxt, items[idx]["id"]))
                conn.commit()
                items[idx]["status"] = nxt
            finally:
                conn.close()


def run_curses():
    """Entry point for curses application."""
    curses.wrapper(run)
