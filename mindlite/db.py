"""Database operations for mindlite."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Item, now_iso

# Default database path
DEFAULT_DB_PATH = str(Path.home() / ".mindlite.db")


def get_db_path() -> str:
    """Get database path from environment or default."""
    return os.environ.get("MINDLITE_DB", DEFAULT_DB_PATH)


def ensure_db() -> sqlite3.Connection:
    """Get database connection, creating file if needed."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn():
    """Context manager for database connections."""
    conn = ensure_db()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize database schema."""
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


def _get_or_create_tags(conn: sqlite3.Connection, names: List[str]) -> List[int]:
    """Get or create tags and return their IDs."""
    tag_ids = []
    for name in names:
        if not name.strip():
            continue
        
        # Try to get existing tag
        cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (name.strip(),))
        row = cursor.fetchone()
        
        if row:
            tag_ids.append(row[0])
        else:
            # Create new tag
            cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (name.strip(),))
            tag_ids.append(cursor.lastrowid)
    
    return tag_ids


def set_item_tags(conn: sqlite3.Connection, item_id: int, tags: List[str]) -> None:
    """Set tags for an item."""
    # Remove existing tags
    conn.execute("DELETE FROM item_tags WHERE item_id = ?", (item_id,))
    
    if tags:
        tag_ids = _get_or_create_tags(conn, tags)
        conn.executemany(
            "INSERT INTO item_tags (item_id, tag_id) VALUES (?, ?)",
            [(item_id, tag_id) for tag_id in tag_ids]
        )


def get_item_tags(conn: sqlite3.Connection, item_id: int) -> List[str]:
    """Get tags for an item."""
    cursor = conn.execute(
        "SELECT t.name FROM tags t JOIN item_tags it ON t.id = it.tag_id WHERE it.item_id = ?",
        (item_id,)
    )
    return [row[0] for row in cursor.fetchall()]


def insert_item(conn: sqlite3.Connection, item: Item) -> int:
    """Insert a new item and return its ID."""
    data = item.to_dict()
    cursor = conn.execute(
        """INSERT INTO items (type, title, body, status, priority, due_date, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            data["type"], data["title"], data["body"], data["status"],
            data["priority"], data["due_date"], data["created_at"], data["updated_at"]
        )
    )
    item_id = cursor.lastrowid
    
    if item.tags:
        set_item_tags(conn, item_id, item.tags)
    
    return item_id


def update_item(conn: sqlite3.Connection, item_id: int, **fields: Any) -> None:
    """Update an item with given fields."""
    if not fields:
        return
    
    # Handle tags separately
    tags = fields.pop("tags", None)
    
    # Update timestamp
    fields["updated_at"] = now_iso()
    
    # Build update query
    set_clauses = [f"{key} = ?" for key in fields.keys()]
    values = list(fields.values()) + [item_id]
    
    conn.execute(
        f"UPDATE items SET {', '.join(set_clauses)} WHERE id = ?",
        values
    )
    
    # Update tags if provided
    if tags is not None:
        set_item_tags(conn, item_id, tags)


def delete_item(conn: sqlite3.Connection, item_id: int) -> None:
    """Delete an item by ID."""
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))


def get_item(conn: sqlite3.Connection, item_id: int) -> Optional[Dict[str, Any]]:
    """Get a single item by ID."""
    cursor = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    
    if not row:
        return None
    
    # Convert to dict and add tags
    item_dict = dict(row)
    item_dict["tags"] = get_item_tags(conn, item_id)
    return item_dict


def list_items(conn: sqlite3.Connection, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """List items with optional filters."""
    if filters is None:
        filters = {}
    
    # Build WHERE clause
    where_parts = []
    params = []
    
    if filters.get("type"):
        where_parts.append("type = ?")
        params.append(filters["type"])
    
    if filters.get("status"):
        where_parts.append("status = ?")
        params.append(filters["status"])
    
    if filters.get("open_only"):
        where_parts.append("status != 'done'")
    
    if filters.get("tag"):
        where_parts.append("id IN (SELECT item_id FROM item_tags WHERE tag_id IN (SELECT id FROM tags WHERE name = ?))")
        params.append(filters["tag"])
    
    if filters.get("search"):
        where_parts.append("(title LIKE ? OR body LIKE ?)")
        search_term = f"%{filters['search']}%"
        params.extend([search_term, search_term])
    
    if filters.get("due_within_days"):
        from datetime import datetime, timedelta
        cutoff_date = (datetime.utcnow() + timedelta(days=filters["due_within_days"])).strftime("%Y-%m-%d")
        where_parts.append("due_date IS NOT NULL AND due_date <= ?")
        params.append(cutoff_date)
    
    # Build query
    where_clause = " AND ".join(where_parts) if where_parts else "1=1"
    query = f"SELECT * FROM items WHERE {where_clause} ORDER BY priority DESC, due_date ASC, created_at DESC"
    
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    
    # Convert to dicts and add tags
    items = []
    for row in rows:
        item_dict = dict(row)
        item_dict["tags"] = get_item_tags(conn, item_dict["id"])
        items.append(item_dict)
    
    return items
