"""Command-line interface for mindlite."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List, Optional

from .db import get_conn, init_db, insert_item, update_item, delete_item, get_item, list_items
from .models import Item, validate_type, validate_status, validate_priority, parse_date
from .utils import comma_split, confirm, print_table, print_item_detail, error_exit
from .export import export_json, export_md
from .tui import run_curses


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
        filters["type"] = comma_split(args.type) if "," in args.type else [args.type]
    if args.status:
        filters["status"] = comma_split(args.status) if "," in args.status else [args.status]
    if args.priority:
        filters["priority"] = comma_split(args.priority) if "," in args.priority else [args.priority]
    if args.open:
        filters["open_only"] = True
    if args.overdue:
        filters["overdue"] = True
    if args.due_today:
        filters["due_today"] = True
    if args.due_this_week:
        filters["due_this_week"] = True
    if args.tag:
        filters["tag"] = args.tag
    if args.tags:
        filters["tag"] = comma_split(args.tags)
    if args.search:
        filters["search"] = args.search
    if args.due_in:
        filters["due_within_days"] = args.due_in
    if args.created_since:
        filters["created_since"] = args.created_since
    if args.updated_since:
        filters["updated_since"] = args.updated_since
    
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


def cmd_bulk(args: argparse.Namespace) -> None:
    """Handle bulk operations."""
    if not args.action:
        error_exit("Bulk action required: done, delete, tag, or start")
    
    # Parse comma-separated IDs
    try:
        ids = [int(id_str.strip()) for id_str in args.ids.split(',')]
    except ValueError:
        error_exit("Invalid IDs. Use comma-separated numbers like: 1,2,3")
    
    with get_conn() as conn:
        # Verify all items exist
        for item_id in ids:
            item = get_item(conn, item_id)
            if not item:
                error_exit(f"Item #{item_id} not found")
        
        # Perform bulk action
        if args.action == 'done':
            for item_id in ids:
                update_item(conn, item_id, status='done')
            print(f"Marked {len(ids)} items as done")
        
        elif args.action == 'delete':
            if not args.yes:
                item_titles = []
                for item_id in ids:
                    item = get_item(conn, item_id)
                    item_titles.append(f"#{item_id} {item['title']}")
                
                prompt = "Delete " + str(len(ids)) + " items?\n" + "\n".join(item_titles)
                if not confirm(prompt):
                    print("Cancelled.")
                    return
            
            for item_id in ids:
                delete_item(conn, item_id)
            print(f"Deleted {len(ids)} items")
        
        elif args.action == 'tag':
            if not args.tags:
                error_exit("Tags required for bulk tag operation")
            
            tags = comma_split(args.tags)
            for item_id in ids:
                item = get_item(conn, item_id)
                existing_tags = item['tags']
                # Merge tags (avoid duplicates)
                all_tags = list(set(existing_tags + tags))
                update_item(conn, item_id, tags=all_tags)
            print(f"Added tags to {len(ids)} items: {', '.join(tags)}")
        
        elif args.action == 'start':
            for item_id in ids:
                update_item(conn, item_id, status='doing')
            print(f"Started {len(ids)} items")
        
        else:
            error_exit(f"Unknown bulk action: {args.action}")


def cmd_help(args: argparse.Namespace) -> None:
    """Show help for commands."""
    if args.command:
        # Show help for specific command
        show_command_help(args.command)
    else:
        # Show general help
        parser = create_parser()
        parser.print_help()
        print("\n" + "="*60)
        print("COMMAND ALIASES:")
        print("="*60)
        aliases = {
            'a': 'add - Add new items',
            'l': 'list - List items with filters', 
            's': 'show - Show item details',
            'e': 'edit - Edit existing items',
            'st': 'start - Start working on items',
            'b': 'block - Block items',
            'del': 'delete - Delete items',
            'ag': 'agenda - Show upcoming items',
            'exp': 'export - Export data',
            'h': 'help - Show this help'
        }
        for alias, description in aliases.items():
            print(f"  {alias:<4} = {description}")
        
        print("\n" + "="*60)
        print("QUICK EXAMPLES:")
        print("="*60)
        examples = [
            "mindlite add \"Task name\" --priority high --due tomorrow",
            "mindlite list --priority high --open",
            "mindlite bulk done 1,2,3",
            "mindlite export json backup.json",
            "mindlite agenda --days 7"
        ]
        for example in examples:
            print(f"  {example}")


def show_command_help(command: str) -> None:
    """Show detailed help for a specific command."""
    help_texts = {
        'add': """
ADD COMMAND - Create new items

Usage: mindlite add "Title" [options]

Required:
  Title                    Item title (use quotes for multi-word titles)

Options:
  --type {todo,idea,issue} Item type (default: todo)
  --body TEXT              Item description/notes
  --priority {low,med,high} Priority level (default: med)
  --tags TEXT              Comma-separated tags
  --due DATE               Due date (multiple formats supported)

Examples:
  mindlite add "Fix login bug" --type issue --priority high --tags bug,urgent
  mindlite add "Research AI tools" --type idea --tags research,ai
  mindlite add "Weekly review" --due +7 --tags recurring
  mindlite add "Call client" --due tomorrow --priority high
""",
        'list': """
LIST COMMAND - Display items with filtering

Usage: mindlite list [options]

Filtering Options:
  --type TYPE              Filter by type (comma-separated: todo,idea,issue)
  --status STATUS          Filter by status (comma-separated: todo,doing,blocked,done)
  --priority PRIORITY      Filter by priority (comma-separated: low,med,high)
  --tags TAGS              Filter by tags (comma-separated)
  --search TEXT            Search in title and body
  --open                   Show only non-done items
  --overdue                Show overdue items
  --due-today              Show items due today
  --due-this-week          Show items due this week
  --due-in DAYS            Show items due within N days
  --created-since DATE     Show items created since date
  --updated-since DATE     Show items updated since date

Examples:
  mindlite list --priority high --open
  mindlite list --tags urgent,work
  mindlite list --due-today
  mindlite list --search "project"
  mindlite list --type todo,idea --status todo,doing
""",
        'bulk': """
BULK COMMAND - Perform operations on multiple items

Usage: mindlite bulk ACTION IDS [options]

Actions:
  done                     Mark items as done
  delete                   Delete items
  tag                      Add tags to items
  start                    Start working on items

Required:
  IDS                      Comma-separated item IDs (e.g., 1,2,3)

Options:
  --tags TAGS              Tags for bulk tag operation
  -y, --yes                Skip confirmation for delete

Examples:
  mindlite bulk done 1,2,3
  mindlite bulk delete 1,2,3 -y
  mindlite bulk tag 1,2 --tags urgent,work
  mindlite bulk start 1,2,3
""",
        'export': """
EXPORT COMMAND - Export data to files

Usage: mindlite export FORMAT OUTPUT

Formats:
  json                     Export as JSON
  md                       Export as Markdown

Examples:
  mindlite export json backup.json
  mindlite export md report.md
""",
        'agenda': """
AGENDA COMMAND - Show upcoming items

Usage: mindlite agenda [options]

Options:
  --days DAYS              Days ahead to show (default: 7)

Examples:
  mindlite agenda
  mindlite agenda --days 14
""",
        'edit': """
EDIT COMMAND - Modify existing items

Usage: mindlite edit ID [options]

Required:
  ID                       Item ID to edit

Options:
  --title TEXT             New title
  --body TEXT              New body/notes
  --type {todo,idea,issue} New type
  --status {todo,doing,blocked,done} New status
  --priority {low,med,high} New priority
  --due DATE               New due date
  --tags TAGS              New tags (comma-separated)

Examples:
  mindlite edit 1 --priority high
  mindlite edit 2 --status doing --tags urgent
  mindlite edit 3 --due tomorrow --body "Updated notes"
"""
    }
    
    if command in help_texts:
        print(help_texts[command])
    else:
        print(f"No detailed help available for command: {command}")
        print("Use 'mindlite help' for general help or 'mindlite {command} --help' for command options.")


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


def cmd_ui(args: argparse.Namespace) -> None:
    """Launch the curses TUI."""
    try:
        run_curses()
    except KeyboardInterrupt:
        print("\nExiting UI...")
    except Exception as e:
        error_exit(f"UI error: {e}")


def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="mindlite",
        description="A minimal CLI for ideas, todos, and issues"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands (aliases: a=add, l=list, s=show, e=edit, st=start, b=block, del=delete, ag=agenda, exp=export, ui=ui, h=help)")
    
    # init command
    subparsers.add_parser("init", help="Initialize database")
    
    # ui command
    subparsers.add_parser("ui", help="Launch curses TUI")
    
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
    list_parser.add_argument("--type", help="Filter by type (comma-separated: todo,idea,issue)")
    list_parser.add_argument("--status", help="Filter by status (comma-separated: todo,doing,blocked,done)")
    list_parser.add_argument("--priority", help="Filter by priority (comma-separated: low,med,high)")
    list_parser.add_argument("--open", action="store_true", help="Show only non-done items")
    list_parser.add_argument("--overdue", action="store_true", help="Show overdue items")
    list_parser.add_argument("--due-today", action="store_true", help="Show items due today")
    list_parser.add_argument("--due-this-week", action="store_true", help="Show items due this week")
    list_parser.add_argument("--tag", help="Filter by tag")
    list_parser.add_argument("--tags", help="Filter by multiple tags (comma-separated)")
    list_parser.add_argument("--search", help="Search in title and body")
    list_parser.add_argument("--due-in", type=int, help="Show items due within N days")
    list_parser.add_argument("--created-since", help="Show items created since date (YYYY-MM-DD)")
    list_parser.add_argument("--updated-since", help="Show items updated since date (YYYY-MM-DD)")
    
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
    
    # bulk command
    bulk_parser = subparsers.add_parser("bulk", help="Bulk operations on multiple items")
    bulk_parser.add_argument("action", choices=["done", "delete", "tag", "start"], help="Bulk action")
    bulk_parser.add_argument("ids", help="Comma-separated item IDs (e.g., 1,2,3)")
    bulk_parser.add_argument("--tags", help="Tags for bulk tag operation")
    bulk_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation for delete")
    
    return parser


def main() -> None:
    """Main entry point."""
    # Handle command aliases before parsing
    command_aliases = {
        'a': 'add',
        'l': 'list', 
        's': 'show',
        'e': 'edit',
        'st': 'start',
        'b': 'block',
        'done': 'done',
        'del': 'delete',
        'ag': 'agenda',
        'exp': 'export',
        'ui': 'ui',
        'h': 'help'
    }
    
    # Handle help commands before parsing
    if len(sys.argv) > 1:
        if sys.argv[1] == 'help':
            if len(sys.argv) > 2:
                # Specific command help
                show_command_help(sys.argv[2])
            else:
                # General help
                cmd_help(type('Args', (), {'command': None})())
            sys.exit(0)
        elif sys.argv[1] in command_aliases:
            sys.argv[1] = command_aliases[sys.argv[1]]
    
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
        "bulk": cmd_bulk,
        "ui": cmd_ui,
        "help": cmd_help,
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
