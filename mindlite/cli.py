"""Command-line interface for mindlite."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List, Optional

from .db import get_conn, init_db, insert_item, update_item, delete_item, get_item, list_items
from .models import Item, validate_type, validate_status, validate_priority, parse_date
from .utils import comma_split, confirm, print_table, print_item_detail, error_exit
from .export import export_json, export_md


def cmd_init(args: argparse.Namespace) -> None:
    """Initialize database."""
    with get_conn() as conn:
        init_db(conn)
    print("Database initialized.")


def cmd_add(args: argparse.Namespace) -> None:
    """Add a new item."""
    try:
        # Validate inputs
        item_type = validate_type(args.type)
        priority = validate_priority(args.priority)
        due_date = parse_date(args.due)
        tags = comma_split(args.tags)
        
        # Create item
        item = Item(
            id=None,
            type=item_type,
            title=args.title,
            body=args.body or "",
            priority=priority,
            due_date=due_date,
            tags=tags
        )
        
        # Insert into database
        with get_conn() as conn:
            item_id = insert_item(conn, item)
        
        print(f"Added item #{item_id}: {item.title}")
        
    except ValueError as e:
        error_exit(str(e))


def cmd_list(args: argparse.Namespace) -> None:
    """List items with optional filters."""
    filters: Dict[str, Any] = {}
    
    if args.type:
        filters["type"] = args.type
    if args.status:
        filters["status"] = args.status
    if args.open:
        filters["open_only"] = True
    if args.tag:
        filters["tag"] = args.tag
    if args.search:
        filters["search"] = args.search
    if args.due_in:
        filters["due_within_days"] = args.due_in
    
    with get_conn() as conn:
        items = list_items(conn, filters)
    
    if not items:
        print("No items found.")
        return
    
    # Define table columns
    columns = [
        ("id", "ID"),
        ("type", "TYPE"),
        ("title", "TITLE"),
        ("status", "STATUS"),
        ("priority", "PRI"),
        ("due_date", "DUE"),
        ("tags", "TAGS")
    ]
    
    # Convert tags list to string for display
    display_items = []
    for item in items:
        display_item = dict(item)
        display_item["tags"] = ", ".join(item["tags"]) if item["tags"] else ""
        display_item["due_date"] = item["due_date"] or ""
        display_items.append(display_item)
    
    print_table(display_items, columns)


def cmd_show(args: argparse.Namespace) -> None:
    """Show detailed view of a single item."""
    with get_conn() as conn:
        item = get_item(conn, args.id)
    
    if not item:
        error_exit(f"Item #{args.id} not found.")
    
    print_item_detail(item)


def cmd_edit(args: argparse.Namespace) -> None:
    """Edit an item."""
    with get_conn() as conn:
        item = get_item(conn, args.id)
    
    if not item:
        error_exit(f"Item #{args.id} not found.")
    
    try:
        # Build update fields
        update_fields: Dict[str, Any] = {}
        
        if args.title is not None:
            update_fields["title"] = args.title
        if args.body is not None:
            update_fields["body"] = args.body
        if args.type is not None:
            update_fields["type"] = validate_type(args.type)
        if args.status is not None:
            update_fields["status"] = validate_status(args.status)
        if args.priority is not None:
            update_fields["priority"] = validate_priority(args.priority)
        if args.due is not None:
            update_fields["due_date"] = parse_date(args.due)
        if args.tags is not None:
            update_fields["tags"] = comma_split(args.tags)
        
        if not update_fields:
            print("No changes specified.")
            return
        
        # Update in database
        with get_conn() as conn:
            update_item(conn, args.id, **update_fields)
        
        print(f"Updated item #{args.id}")
        
    except ValueError as e:
        error_exit(str(e))


def cmd_status_change(args: argparse.Namespace, new_status: str) -> None:
    """Change item status."""
    with get_conn() as conn:
        item = get_item(conn, args.id)
    
    if not item:
        error_exit(f"Item #{args.id} not found.")
    
    try:
        validated_status = validate_status(new_status)
        with get_conn() as conn:
            update_item(conn, args.id, status=validated_status)
        
        print(f"Item #{args.id} status changed to {validated_status}")
        
    except ValueError as e:
        error_exit(str(e))


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete an item."""
    with get_conn() as conn:
        item = get_item(conn, args.id)
    
    if not item:
        error_exit(f"Item #{args.id} not found.")
    
    if not args.yes and not confirm(f"Delete item #{args.id} '{item['title']}'?"):
        print("Cancelled.")
        return
    
    with get_conn() as conn:
        delete_item(conn, args.id)
    
    print(f"Deleted item #{args.id}")


def cmd_agenda(args: argparse.Namespace) -> None:
    """Show agenda (items due within specified days)."""
    days = args.days or 7
    
    filters = {
        "open_only": True,
        "due_within_days": days
    }
    
    with get_conn() as conn:
        items = list_items(conn, filters)
    
    if not items:
        print(f"No items due within {days} days.")
        return
    
    print(f"Items due within {days} days:")
    print()
    
    # Use same table format as list command
    columns = [
        ("id", "ID"),
        ("type", "TYPE"),
        ("title", "TITLE"),
        ("status", "STATUS"),
        ("priority", "PRI"),
        ("due_date", "DUE"),
        ("tags", "TAGS")
    ]
    
    display_items = []
    for item in items:
        display_item = dict(item)
        display_item["tags"] = ", ".join(item["tags"]) if item["tags"] else ""
        display_items.append(display_item)
    
    print_table(display_items, columns)


def cmd_export(args: argparse.Namespace) -> None:
    """Export items to file."""
    with get_conn() as conn:
        if args.format == "json":
            export_json(conn, args.output)
        elif args.format == "md":
            export_md(conn, args.output)
        else:
            error_exit(f"Unsupported format: {args.format}")
    
    print(f"Exported to {args.output}")


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="mindlite",
        description="A minimal CLI for ideas, todos, and issues"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # init command
    subparsers.add_parser("init", help="Initialize database")
    
    # add command
    add_parser = subparsers.add_parser("add", help="Add a new item")
    add_parser.add_argument("title", help="Item title")
    add_parser.add_argument("--type", choices=["todo", "idea", "issue"], default="todo", help="Item type")
    add_parser.add_argument("--body", help="Item body/notes")
    add_parser.add_argument("--priority", choices=["low", "med", "high"], default="med", help="Priority")
    add_parser.add_argument("--tags", help="Comma-separated tags")
    add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List items")
    list_parser.add_argument("--type", choices=["todo", "idea", "issue"], help="Filter by type")
    list_parser.add_argument("--status", choices=["todo", "doing", "blocked", "done"], help="Filter by status")
    list_parser.add_argument("--open", action="store_true", help="Show only non-done items")
    list_parser.add_argument("--tag", help="Filter by tag")
    list_parser.add_argument("--search", help="Search in title and body")
    list_parser.add_argument("--due-in", type=int, help="Show items due within N days")
    
    # show command
    show_parser = subparsers.add_parser("show", help="Show item details")
    show_parser.add_argument("id", type=int, help="Item ID")
    
    # edit command
    edit_parser = subparsers.add_parser("edit", help="Edit an item")
    edit_parser.add_argument("id", type=int, help="Item ID")
    edit_parser.add_argument("--title", help="New title")
    edit_parser.add_argument("--body", help="New body")
    edit_parser.add_argument("--type", choices=["todo", "idea", "issue"], help="New type")
    edit_parser.add_argument("--status", choices=["todo", "doing", "blocked", "done"], help="New status")
    edit_parser.add_argument("--priority", choices=["low", "med", "high"], help="New priority")
    edit_parser.add_argument("--due", help="New due date (YYYY-MM-DD)")
    edit_parser.add_argument("--tags", help="New tags (comma-separated)")
    
    # status change commands
    start_parser = subparsers.add_parser("start", help="Start working on an item")
    start_parser.add_argument("id", type=int, help="Item ID")
    
    block_parser = subparsers.add_parser("block", help="Block an item")
    block_parser.add_argument("id", type=int, help="Item ID")
    
    done_parser = subparsers.add_parser("done", help="Mark item as done")
    done_parser.add_argument("id", type=int, help="Item ID")
    
    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an item")
    delete_parser.add_argument("id", type=int, help="Item ID")
    delete_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    
    # agenda command
    agenda_parser = subparsers.add_parser("agenda", help="Show agenda")
    agenda_parser.add_argument("--days", type=int, help="Days ahead to show (default: 7)")
    
    # export command
    export_parser = subparsers.add_parser("export", help="Export items")
    export_parser.add_argument("format", choices=["json", "md"], help="Export format")
    export_parser.add_argument("output", help="Output file path")
    
    return parser


def main() -> None:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route to appropriate command handler
    command_handlers = {
        "init": cmd_init,
        "add": cmd_add,
        "list": cmd_list,
        "show": cmd_show,
        "edit": cmd_edit,
        "start": lambda args: cmd_status_change(args, "doing"),
        "block": lambda args: cmd_status_change(args, "blocked"),
        "done": lambda args: cmd_status_change(args, "done"),
        "delete": cmd_delete,
        "agenda": cmd_agenda,
        "export": cmd_export,
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        try:
            handler(args)
        except KeyboardInterrupt:
            print("\nCancelled.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            error_exit(f"Unexpected error: {e}")
    else:
        error_exit(f"Unknown command: {args.command}")
