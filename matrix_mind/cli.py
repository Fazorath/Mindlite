from __future__ import annotations

import json
from datetime import datetime
from typing import Optional, List

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.tree import Tree

from . import __version__
from .models import Item
from . import db as dbm

app = typer.Typer(add_completion=False, help="Matrix Mind CLI")
console = Console(theme=None)


def _accent(text: str) -> str:
    return f"[bold #00E676]{text}[/]"


@app.callback()
def version_callback(
    version: Optional[bool] = typer.Option(
        None, "--version", help="Show version and exit", is_eager=True
    )
):
    if version:
        console.print(_accent(f"matrix-mind v{__version__}"))
        raise typer.Exit()


@app.command()
def init():
    """Create database tables (idempotent)."""
    dbm.init_db()
    console.print(Panel.fit(_accent("Database initialized")))


@app.command()
def add(
    title: str = typer.Argument(..., help="Title for the item"),
    type: str = typer.Option("todo", "--type", "-t", help="Item type"),
    body: str = typer.Option("", "--body", "-b", help="Body/notes"),
    priority: str = typer.Option("med", "--priority", "-p", help="Priority"),
    tags: str = typer.Option("", "--tags", "-g", help="Comma-separated tags"),
    due: Optional[str] = typer.Option(None, "--due", help="Due date YYYY-MM-DD"),
):
    item = Item(
        id=None,
        type=type,  # type: ignore[arg-type]
        title=title,
        body=body,
        priority=priority,  # type: ignore[arg-type]
        due_date=due,
        tags=[t.strip() for t in tags.split(",") if t.strip()] if tags else [],
    )
    item_id = dbm.add_item(item)
    console.print(Panel.fit(_accent(f"Added #{item_id}: {title}")))


def _render_table(rows):
    table = Table(title=_accent("Items"), show_lines=False, header_style="#00E676")
    table.add_column("ID", justify="right")
    table.add_column("Type")
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Priority")
    table.add_column("Due")
    table.add_column("Tags")
    for r in rows:
        status_color = {
            "todo": "#00BFA5",
            "doing": "#00E676",
            "blocked": "red3",
            "done": "gray62",
        }.get(r["status"], "white")
        table.add_row(
            str(r["id"]),
            r["type"],
            r["title"],
            f"[{status_color}]{r['status']}[/]",
            r["priority"],
            r["due_date"] or "",
            r["tags"],
        )
    console.print(table)


@app.command()
def list(
    type: Optional[List[str]] = typer.Option(None, "--type"),
    status: Optional[List[str]] = typer.Option(None, "--status"),
    open: bool = typer.Option(False, "--open", help="Only non-done"),
    tag: Optional[str] = typer.Option(None, "--tag"),
    search: Optional[str] = typer.Option(None, "--search"),
    due_in: Optional[int] = typer.Option(None, "--due-in"),
):
    rows = dbm.list_items(
        types=type, statuses=status, open_only=open, tag=tag, search=search, due_in=due_in
    )
    _render_table(rows)


@app.command()
def show(id: int):
    row = dbm.get_item(id)
    if not row:
        console.print(Panel.fit(f"[red]Item #{id} not found"))
        raise typer.Exit(1)
    meta = f"Type: {row['type']}  |  Status: {row['status']}  |  Priority: {row['priority']}\nDue: {row['due_date'] or '-'}  |  Tags: {row['tags']}\nCreated: {row['created_at']}  Updated: {row['updated_at']}"
    console.print(Panel(row["body"] or "(no body)", title=_accent(f"#{row['id']} {row['title']}"), subtitle=meta))


@app.command()
def edit(
    id: int,
    title: Optional[str] = typer.Option(None, "--title"),
    body: Optional[str] = typer.Option(None, "--body"),
    type: Optional[str] = typer.Option(None, "--type"),
    priority: Optional[str] = typer.Option(None, "--priority"),
    due: Optional[str] = typer.Option(None, "--due"),
    tags: Optional[str] = typer.Option(None, "--tags"),
):
    fields = {}
    if title is not None:
        fields["title"] = title
    if body is not None:
        fields["body"] = body
    if type is not None:
        fields["type"] = type
    if priority is not None:
        fields["priority"] = priority
    if due is not None:
        fields["due_date"] = due
    if tags is not None:
        fields["tags"] = [t.strip() for t in tags.split(',') if t.strip()]
    dbm.update_item(id, **fields)
    console.print(Panel.fit(_accent(f"Updated #{id}")))


@app.command()
def start(id: int):
    dbm.set_status(id, "doing")
    console.print(Panel.fit(_accent(f"#{id} → doing")))


@app.command()
def block(id: int):
    dbm.set_status(id, "blocked")
    console.print(Panel.fit(_accent(f"#{id} → blocked")))


@app.command()
def done(id: int):
    dbm.set_status(id, "done")
    console.print(Panel.fit(_accent(f"#{id} → done")))


@app.command()
def delete(id: int, y: bool = typer.Option(False, "-y", help="Confirm")):
    if not y:
        typer.confirm(f"Delete item #{id}?", abort=True)
    dbm.delete_item(id)
    console.print(Panel.fit(_accent(f"Deleted #{id}")))


@app.command()
def board():
    rows = dbm.list_items()
    columns = {"todo": [], "doing": [], "blocked": [], "done": []}
    for r in rows:
        columns[r["status"]].append(r)
    rendered = []
    for col in ["todo", "doing", "blocked", "done"]:
        inner = Table(title=_accent(col.upper()), show_header=False, box=None)
        inner.add_column("Card")
        for r in columns[col]:
            inner.add_row(f"[bold]{r['id']}[/] {r['title']} [dim]({r['tags']})[/]")
        rendered.append(inner)
    console.print(Columns(rendered, expand=True))


@app.command()
def agenda(days: int = typer.Option(7, "--days")):
    rows = dbm.list_items(open_only=True, due_in=days)
    _render_table(rows)


@app.command()
def map(by: str = typer.Option("tag", "--by", help="Group by tag|type")):
    if by == "type":
        rows = dbm.list_items()
        root = Tree(_accent("Map by Type"))
        types = {"todo": [], "idea": [], "issue": []}
        for r in rows:
            types[r["type"]].append(r)
        for t, items in types.items():
            node = root.add(f"[bold]{t}")
            for r in items:
                node.add(f"#{r['id']} {r['title']}")
        console.print(root)
        return
    # by tag
    rows = dbm.list_items()
    tag_to_items: dict[str, list] = {}
    for r in rows:
        for tag in filter(None, (r["tags"] or "").split(",")):
            tag_to_items.setdefault(tag, []).append(r)
    root = Tree(_accent("Map by Tag"))
    for tag, items in sorted(tag_to_items.items()):
        node = root.add(f"[bold]{tag}")
        for r in items:
            node.add(f"#{r['id']} {r['title']} [{r['type']}] ({r['status']})")
    console.print(root)


@app.command("export")
def export_cmd(fmt: str, out_path: str):
    from .export import export_json, export_markdown

    rows = dbm.list_items()
    if fmt == "json":
        export_json(rows, out_path)
    elif fmt == "md":
        export_markdown(rows, out_path)
    else:
        console.print("[red]Unsupported format. Use md|json")
        raise typer.Exit(1)
    console.print(Panel.fit(_accent(f"Exported to {out_path}")))


if __name__ == "__main__":
    app()


