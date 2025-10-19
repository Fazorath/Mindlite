#!/usr/bin/env python3
"""Mindlite - Single-file executable."""

import sys
import os
import sqlite3
import argparse
import json
import re
from contextlib import contextmanager
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Literal, Tuple

# Configuration
DEFAULT_DB_PATH = str(Path.home() / ".mindlite.db")

# Type aliases
ItemType = Literal["todo", "idea", "issue"]
ItemStatus = Literal["todo", "doing", "blocked", "done"]
Priority = Literal["low", "med", "high"]

def get_db_path() -> str:
    return os.environ.get("MINDLITE_DB", DEFAULT_DB_PATH)

def ensure_db() -> sqlite3.Connection:
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def get_conn():
    conn = ensure_db()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db(conn: sqlite3.Connection) -> None:
    schema = """
    CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('todo','idea','issue')),
        title TEXT NOT NULL,
        body TEXT DEFAULT '',
        status TEXT NOT NULL DEFAULT 'todo' CHECK (status IN ('todo','doing','blocked','done')),
        priority TEXT NOT NULL DEFAULT 'med' CHECK (priority IN ('low','med','high')),
        due_date TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS tags(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS item_tags(
        item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
        tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY(item_id, tag_id)
    );
    """
    conn.executescript(schema)

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat() + "Z"

def parse_date(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        raise ValueError(f"Invalid date format: {s}. Use YYYY-MM-DD")
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError as e:
        raise ValueError(f"Invalid date: {s}. {e}")

def validate_type(item_type: str) -> ItemType:
    if item_type not in ("todo", "idea", "issue"):
        raise ValueError(f"Invalid type: {item_type}. Must be one of: todo, idea, issue")
    return item_type

def validate_status(status: str) -> ItemStatus:
    if status not in ("todo", "doing", "blocked", "done"):
        raise ValueError(f"Invalid status: {status}. Must be one of: todo, doing, blocked, done")
    return status

def validate_priority(priority: str) -> Priority:
    if priority not in ("low", "med", "high"):
        raise ValueError(f"Invalid priority: {priority}. Must be one of: low, med, high")
    return priority

def comma_split(s: Optional[str]) -> List[str]:
    if not s:
        return []
    return [item.strip() for item in s.split(",") if item.strip()]

def confirm(prompt: str) -> bool:
    while True:
        response = input(f"{prompt} [y/N]: ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no", ""):
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def print_table(rows: List[dict], columns: List[Tuple[str, str]]) -> None:
    if not rows:
        print("No items found.")
        return
    
    # Get terminal width for better column sizing
    import shutil
    terminal_width = shutil.get_terminal_size().columns
    
    # Calculate column widths more intelligently
    widths = {}
    for field_name, display_name in columns:
        # Start with header width
        widths[field_name] = len(display_name)
    
    # Calculate content widths
    for row in rows:
        for field_name, _ in columns:
            value = str(row.get(field_name, ""))
            # Don't truncate during width calculation
            widths[field_name] = max(widths[field_name], len(value))
    
    # Distribute available width proportionally
    total_content_width = sum(widths.values())
    available_width = terminal_width - (len(columns) - 1) * 3  # Account for separators
    
    if total_content_width > available_width:
        # Scale down proportionally, but keep minimum widths
        scale_factor = available_width / total_content_width
        for field_name in widths:
            new_width = max(8, int(widths[field_name] * scale_factor))
            widths[field_name] = min(new_width, widths[field_name])  # Don't make wider than content
    
    # Print header
    header_parts = []
    separator_parts = []
    for field_name, display_name in columns:
        width = widths[field_name]
        header_parts.append(display_name.ljust(width))
        separator_parts.append("-" * width)
    
    print(" | ".join(header_parts))
    print("-+-".join(separator_parts))
    
    # Print rows
    for row in rows:
        row_parts = []
        for field_name, _ in columns:
            value = str(row.get(field_name, ""))
            width = widths[field_name]
            # Truncate with ellipsis if needed
            if len(value) > width:
                value = value[:width-3] + "..."
            row_parts.append(value.ljust(width))
        print(" | ".join(row_parts))

def print_item_detail(item: dict) -> None:
    print(f"#{item['id']} {item['title']}")
    print("=" * (len(str(item['id'])) + len(item['title']) + 2))
    print(f"Type: {item['type']}")
    print(f"Status: {item['status']}")
    print(f"Priority: {item['priority']}")
    print(f"Due: {item['due_date'] or 'Not set'}")
    print(f"Tags: {', '.join(item['tags']) if item['tags'] else 'None'}")
    print(f"Created: {item['created_at']}")
    print(f"Updated: {item['updated_at']}")
    if item['body']:
        print("\nBody:")
        print(item['body'])
    else:
        print("\nNo body text.")

def error_exit(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)

# Database operations
def _get_or_create_tags(conn: sqlite3.Connection, names: List[str]) -> List[int]:
    tag_ids = []
    for name in names:
        if not name.strip():
            continue
        cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (name.strip(),))
        row = cursor.fetchone()
        if row:
            tag_ids.append(row[0])
        else:
            cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (name.strip(),))
            tag_ids.append(cursor.lastrowid)
    return tag_ids

def set_item_tags(conn: sqlite3.Connection, item_id: int, tags: List[str]) -> None:
    conn.execute("DELETE FROM item_tags WHERE item_id = ?", (item_id,))
    if tags:
        tag_ids = _get_or_create_tags(conn, tags)
        conn.executemany(
            "INSERT INTO item_tags (item_id, tag_id) VALUES (?, ?)",
            [(item_id, tag_id) for tag_id in tag_ids]
        )

def get_item_tags(conn: sqlite3.Connection, item_id: int) -> List[str]:
    cursor = conn.execute(
        "SELECT t.name FROM tags t JOIN item_tags it ON t.id = it.tag_id WHERE it.item_id = ?",
        (item_id,)
    )
    return [row[0] for row in cursor.fetchall()]

def insert_item(conn: sqlite3.Connection, item_data: dict) -> int:
    # Check if this is the first item (database is empty)
    cursor = conn.execute('SELECT COUNT(*) FROM items')
    count = cursor.fetchone()[0]
    
    cursor = conn.execute(
        """INSERT INTO items (type, title, body, status, priority, due_date, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            item_data["type"], item_data["title"], item_data["body"], item_data["status"],
            item_data["priority"], item_data["due_date"], item_data["created_at"], item_data["updated_at"]
        )
    )
    item_id = cursor.lastrowid
    
    # If this was the first item, reset the autoincrement to start from 1
    if count == 0:
        conn.execute('DELETE FROM sqlite_sequence WHERE name="items"')
        conn.execute('UPDATE items SET id = 1 WHERE id = ?', (item_id,))
        item_id = 1
    
    if item_data.get("tags"):
        set_item_tags(conn, item_id, item_data["tags"])
    return item_id

def update_item(conn: sqlite3.Connection, item_id: int, **fields: Any) -> None:
    if not fields:
        return
    tags = fields.pop("tags", None)
    fields["updated_at"] = now_iso()
    set_clauses = [f"{key} = ?" for key in fields.keys()]
    values = list(fields.values()) + [item_id]
    conn.execute(f"UPDATE items SET {', '.join(set_clauses)} WHERE id = ?", values)
    if tags is not None:
        set_item_tags(conn, item_id, tags)

def delete_item(conn: sqlite3.Connection, item_id: int) -> None:
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))

def get_item(conn: sqlite3.Connection, item_id: int) -> Optional[Dict[str, Any]]:
    cursor = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if not row:
        return None
    item_dict = dict(row)
    item_dict["tags"] = get_item_tags(conn, item_id)
    return item_dict

def list_items(conn: sqlite3.Connection, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if filters is None:
        filters = {}
    
    # Build WHERE clause
    where_parts = []
    params = []
    
    if filters.get('type'):
        types = filters['type'] if isinstance(filters['type'], list) else [filters['type']]
        placeholders = ','.join(['?' for _ in types])
        where_parts.append(f'type IN ({placeholders})')
        params.extend(types)
    
    if filters.get('status'):
        statuses = filters['status'] if isinstance(filters['status'], list) else [filters['status']]
        placeholders = ','.join(['?' for _ in statuses])
        where_parts.append(f'status IN ({placeholders})')
        params.extend(statuses)
    
    if filters.get('priority'):
        priorities = filters['priority'] if isinstance(filters['priority'], list) else [filters['priority']]
        placeholders = ','.join(['?' for _ in priorities])
        where_parts.append(f'priority IN ({placeholders})')
        params.extend(priorities)
    
    if filters.get('open_only'):
        where_parts.append("status != 'done'")
    
    if filters.get('overdue'):
        from datetime import datetime
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        where_parts.append(f'due_date < ?')
        params.append(today)
    
    if filters.get('due_today'):
        from datetime import datetime
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        where_parts.append(f'due_date = ?')
        params.append(today)
    
    if filters.get('due_this_week'):
        from datetime import datetime, timedelta
        today = datetime.now(timezone.utc)
        week_end = (today + timedelta(days=7)).strftime('%Y-%m-%d')
        where_parts.append(f'due_date <= ? AND due_date >= ?')
        params.extend([week_end, today.strftime('%Y-%m-%d')])
    
    if filters.get('tag'):
        tags = filters['tag'] if isinstance(filters['tag'], list) else [filters['tag']]
        tag_conditions = []
        for tag in tags:
            tag_conditions.append('id IN (SELECT item_id FROM item_tags WHERE tag_id IN (SELECT id FROM tags WHERE name = ?))')
            params.append(tag)
        where_parts.append(f'({' OR '.join(tag_conditions)})')
    
    if filters.get('search'):
        where_parts.append('(title LIKE ? OR body LIKE ?)')
        search_term = f'%{filters["search"]}%'
        params.extend([search_term, search_term])
    
    if filters.get('due_within_days'):
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now(timezone.utc) + timedelta(days=filters['due_within_days'])).strftime('%Y-%m-%d')
        where_parts.append('due_date IS NOT NULL AND due_date <= ?')
        params.append(cutoff_date)
    
    if filters.get('created_since'):
        where_parts.append('created_at >= ?')
        params.append(filters['created_since'])
    
    if filters.get('updated_since'):
        where_parts.append('updated_at >= ?')
        params.append(filters['updated_since'])
    
    # Build query
    where_clause = ' AND '.join(where_parts) if where_parts else '1=1'
    query = f'SELECT * FROM items WHERE {where_clause} ORDER BY id ASC'
    
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    
    # Convert to dicts and add tags
    items = []
    for row in rows:
        item_dict = dict(row)
        item_dict['tags'] = get_item_tags(conn, item_dict['id'])
        items.append(item_dict)
    
    return items

# Command handlers
def cmd_init(args: argparse.Namespace) -> None:
    with get_conn() as conn:
        init_db(conn)
    print("Database initialized.")

def cmd_add(args: argparse.Namespace) -> None:
    try:
        item_type = validate_type(args.type)
        priority = validate_priority(args.priority)
        due_date = parse_date(args.due)
        tags = comma_split(args.tags)
        
        item_data = {
            "type": item_type,
            "title": args.title,
            "body": args.body or "",
            "status": "todo",
            "priority": priority,
            "due_date": due_date,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "tags": tags
        }
        
        with get_conn() as conn:
            item_id = insert_item(conn, item_data)
        
        print(f"Added item #{item_id}: {item_data['title']}")
        
    except ValueError as e:
        error_exit(str(e))

def cmd_list(args: argparse.Namespace) -> None:
    filters: Dict[str, Any] = {}
    
    if args.type:
        filters['type'] = args.type
    if args.status:
        filters["status"] = comma_split(args.status) if "," in args.status else [args.status]
        filters['status'] = args.status
    if args.priority:
        filters["priority"] = comma_split(args.priority) if "," in args.priority else [args.priority]
    if args.open:
        filters['open_only'] = True
    if args.overdue:
        filters['overdue'] = True
    if args.due_today:
        filters['due_today'] = True
    if args.due_this_week:
        filters['due_this_week'] = True
    if args.tag:
        filters['tag'] = args.tag
    if args.tags:
        filters['tag'] = comma_split(args.tags)
    if args.search:
        filters['search'] = args.search
    if args.due_in:
        filters['due_within_days'] = args.due_in
    if args.created_since:
        filters['created_since'] = args.created_since
    if args.updated_since:
        filters['updated_since'] = args.updated_since
    
    with get_conn() as conn:
        items = list_items(conn, filters)
    
    if not items:
        print('No items found.')
        return
    
    columns = [
        ('id', 'ID'),
        ('type', 'TYPE'),
        ('title', 'TITLE'),
        ('status', 'STATUS'),
        ('priority', 'PRI'),
        ('due_date', 'DUE'),
        ('tags', 'TAGS')
    ]
    
    display_items = []
    for item in items:
        display_item = dict(item)
        display_item['tags'] = ', '.join(item['tags']) if item['tags'] else ''
        display_item['due_date'] = item['due_date'] or ''
        display_items.append(display_item)
    
    print_table(display_items, columns)

def cmd_show(args: argparse.Namespace) -> None:
    with get_conn() as conn:
        item = get_item(conn, args.id)
    
    if not item:
        error_exit(f"Item #{args.id} not found.")
    
    print_item_detail(item)

def cmd_edit(args: argparse.Namespace) -> None:
    with get_conn() as conn:
        item = get_item(conn, args.id)
    
    if not item:
        error_exit(f"Item #{args.id} not found.")
    
    try:
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
        
        with get_conn() as conn:
            update_item(conn, args.id, **update_fields)
        
        print(f"Updated item #{args.id}")
        
    except ValueError as e:
        error_exit(str(e))

def cmd_status_change(args: argparse.Namespace, new_status: str) -> None:
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


def cmd_export(args: argparse.Namespace) -> None:
    with get_conn() as conn:
        items = list_items(conn)
    
    if args.format == "json":
        export_data = []
        for item in items:
            export_item = dict(item)
            export_data.append(export_item)
        
        output_path = Path(args.output)
        output_path.write_text(json.dumps(export_data, indent=2), encoding="utf-8")
    elif args.format == "md":
        lines = ["# Mindlite Export\n"]
        
        for item in items:
            lines.append(f"## #{item['id']} {item['title']}")
            lines.append(f"- Type: {item['type']}")
            lines.append(f"- Status: {item['status']}")
            lines.append(f"- Priority: {item['priority']}")
            lines.append(f"- Due: {item['due_date'] or 'Not set'}")
            lines.append(f"- Tags: {', '.join(item['tags']) if item['tags'] else 'None'}")
            lines.append(f"- Created: {item['created_at']}")
            lines.append(f"- Updated: {item['updated_at']}")
            
            if item['body']:
                lines.append("\n" + item['body'])
            else:
                lines.append("\nNo body text.")
            
            lines.append("\n---\n")
        
        output_path = Path(args.output)
        output_path.write_text("\n".join(lines), encoding="utf-8")
    else:
        error_exit(f"Unsupported format: {args.format}")
    
    print(f"Exported to {args.output}")

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mindlite",
        description="A minimal CLI for ideas, todos, and issues"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    subparsers.add_parser("init", help="Initialize database")
    
    add_parser = subparsers.add_parser("add", help="Add a new item")
    add_parser.add_argument("title", help="Item title")
    add_parser.add_argument("--type", choices=["todo", "idea", "issue"], default="todo", help="Item type")
    add_parser.add_argument("--body", help="Item body/notes")
    add_parser.add_argument("--priority", choices=["low", "med", "high"], default="med", help="Priority")
    add_parser.add_argument("--tags", help="Comma-separated tags")
    add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")
    
    list_parser = subparsers.add_parser("list", help="List items")
    list_parser.add_argument("--type", choices=["todo", "idea", "issue"], help="Filter by type")
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
    
    show_parser = subparsers.add_parser("show", help="Show item details")
    show_parser.add_argument("id", type=int, help="Item ID")
    
    edit_parser = subparsers.add_parser("edit", help="Edit an item")
    edit_parser.add_argument("id", type=int, help="Item ID")
    edit_parser.add_argument("--title", help="New title")
    edit_parser.add_argument("--body", help="New body")
    edit_parser.add_argument("--type", choices=["todo", "idea", "issue"], help="New type")
    edit_parser.add_argument("--status", choices=["todo", "doing", "blocked", "done"], help="New status")
    edit_parser.add_argument("--priority", choices=["low", "med", "high"], help="New priority")
    edit_parser.add_argument("--due", help="New due date (YYYY-MM-DD)")
    edit_parser.add_argument("--tags", help="New tags (comma-separated)")
    
    start_parser = subparsers.add_parser("start", help="Start working on an item")
    start_parser.add_argument("id", type=int, help="Item ID")
    
    block_parser = subparsers.add_parser("block", help="Block an item")
    block_parser.add_argument("id", type=int, help="Item ID")
    
    done_parser = subparsers.add_parser("done", help="Mark item as done")
    done_parser.add_argument("id", type=int, help="Item ID")
    
    delete_parser = subparsers.add_parser("delete", help="Delete an item")
    delete_parser.add_argument("id", type=int, help="Item ID")
    delete_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    
    agenda_parser = subparsers.add_parser("agenda", help="Show agenda")
    agenda_parser.add_argument("--days", type=int, help="Days ahead to show (default: 7)")
    
    export_parser = subparsers.add_parser("export", help="Export items")
    bulk_parser = subparsers.add_parser("bulk", help="Bulk operations on multiple items")
    bulk_parser.add_argument("action", choices=["done", "delete", "tag", "start"], help="Bulk action")
    bulk_parser.add_argument("ids", help="Comma-separated item IDs (e.g., 1,2,3)")
    bulk_parser.add_argument("--tags", help="Tags for bulk tag operation")
    bulk_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation for delete")
    subparsers.add_parser("help", help="Show help")
    export_parser.add_argument("format", choices=["json", "md"], help="Export format")
    export_parser.add_argument("output", help="Output file path")
    
    return parser

def main() -> None:
    parser = create_parser()
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
        'h': 'help'
    }
    
    # Replace aliases in sys.argv before parsing
    if len(sys.argv) > 1 and sys.argv[1] in command_aliases:
        sys.argv[1] = command_aliases[sys.argv[1]]
    
    args = parser.parse_args()
    
    if args.command == 'help':
        parser.print_help()
        sys.exit(0)
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
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

if __name__ == "__main__":
    main()
