from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator, Iterable, List, Optional, Sequence, Tuple, Dict, Any

from .models import Item, ItemType, ItemStatus, Priority, utc_now_iso


DEFAULT_DB_PATH = str(Path.home() / ".matrix_mind.db")


def get_db_path() -> str:
    return os.environ.get("MIND_DB", DEFAULT_DB_PATH)


def _connect(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    conn = _connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


SCHEMA = {
    "items": (
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK (type IN ('todo','idea','issue')),
            title TEXT NOT NULL,
            body TEXT DEFAULT '',
            status TEXT NOT NULL CHECK (status IN ('todo','doing','blocked','done')) DEFAULT 'todo',
            priority TEXT NOT NULL CHECK (priority IN ('low','med','high')) DEFAULT 'med',
            due_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    ),
    "tags": (
        """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    ),
    "item_tags": (
        """
        CREATE TABLE IF NOT EXISTS item_tags (
            item_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (item_id, tag_id),
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
        """
    ),
}


def init_db(db_path: Optional[str] = None) -> None:
    with get_conn(db_path) as conn:
        cur = conn.cursor()
        for sql in SCHEMA.values():
            cur.execute(sql)


def _ensure_tags(conn: sqlite3.Connection, tag_names: Iterable[str]) -> Dict[str, int]:
    tag_to_id: Dict[str, int] = {}
    for name in [t.strip() for t in tag_names if t and t.strip()]:
        cur = conn.execute("INSERT OR IGNORE INTO tags(name) VALUES (?)", (name,))
        # fetch id
        row = conn.execute("SELECT id FROM tags WHERE name=?", (name,)).fetchone()
        if row:
            tag_to_id[name] = int(row[0])
    return tag_to_id


def add_item(item: Item, db_path: Optional[str] = None) -> int:
    with get_conn(db_path) as conn:
        cur = conn.execute(
            (
                "INSERT INTO items(type,title,body,status,priority,due_date,created_at,updated_at)"
                " VALUES(?,?,?,?,?,?,?,?)"
            ),
            (
                item.type,
                item.title,
                item.body,
                item.status,
                item.priority,
                item.due_date,
                item.created_at,
                item.updated_at,
            ),
        )
        item_id = int(cur.lastrowid)
        if item.tags:
            tag_to_id = _ensure_tags(conn, item.tags)
            conn.executemany(
                "INSERT OR IGNORE INTO item_tags(item_id, tag_id) VALUES (?,?)",
                [(item_id, tag_id) for tag_id in tag_to_id.values()],
            )
        return item_id


def _apply_filters(where: List[str], params: List[Any], *,
                   types: Optional[Sequence[str]] = None,
                   statuses: Optional[Sequence[str]] = None,
                   open_only: bool = False,
                   tag: Optional[str] = None,
                   search: Optional[str] = None,
                   due_in: Optional[int] = None) -> Tuple[List[str], List[Any]]:
    if types:
        where.append(f"items.type IN ({','.join('?' for _ in types)})")
        params.extend(types)
    if statuses:
        where.append(f"items.status IN ({','.join('?' for _ in statuses)})")
        params.extend(statuses)
    if open_only:
        where.append("items.status != 'done'")
    if tag:
        where.append("EXISTS (SELECT 1 FROM item_tags it JOIN tags t ON t.id=it.tag_id WHERE it.item_id=items.id AND t.name=?)")
        params.append(tag)
    if search:
        like = f"%{search}%"
        where.append("(items.title LIKE ? OR items.body LIKE ?)")
        params.extend([like, like])
    if due_in is not None:
        until = (datetime.utcnow() + timedelta(days=due_in)).date().isoformat()
        where.append("items.due_date IS NOT NULL AND items.due_date <= ?")
        params.append(until)
    return where, params


def list_items(*, types: Optional[Sequence[str]] = None,
               statuses: Optional[Sequence[str]] = None,
               open_only: bool = False,
               tag: Optional[str] = None,
               search: Optional[str] = None,
               due_in: Optional[int] = None,
               db_path: Optional[str] = None) -> List[sqlite3.Row]:
    with get_conn(db_path) as conn:
        where: List[str] = []
        params: List[Any] = []
        where, params = _apply_filters(where, params, types=types, statuses=statuses,
                                       open_only=open_only, tag=tag, search=search, due_in=due_in)
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""
        sql = (
            "SELECT items.*, COALESCE(GROUP_CONCAT(tags.name, ','), '') AS tags "
            "FROM items "
            "LEFT JOIN item_tags ON items.id = item_tags.item_id "
            "LEFT JOIN tags ON tags.id = item_tags.tag_id "
            f"{where_sql} "
            "GROUP BY items.id "
            "ORDER BY CASE priority WHEN 'high' THEN 0 WHEN 'med' THEN 1 ELSE 2 END, "
            "due_date IS NULL, due_date ASC, updated_at DESC"
        )
        cur = conn.execute(sql, params)
        return list(cur.fetchall())


def get_item(item_id: int, db_path: Optional[str] = None) -> Optional[sqlite3.Row]:
    with get_conn(db_path) as conn:
        row = conn.execute(
            (
                "SELECT items.*, COALESCE(GROUP_CONCAT(tags.name, ','), '') AS tags "
                "FROM items "
                "LEFT JOIN item_tags ON items.id = item_tags.item_id "
                "LEFT JOIN tags ON tags.id = item_tags.tag_id "
                "WHERE items.id=? GROUP BY items.id"
            ),
            (item_id,),
        ).fetchone()
        return row


def update_item(item_id: int, **fields: Any) -> None:
    if not fields:
        return
    tags = fields.pop("tags", None)
    fields["updated_at"] = utc_now_iso()
    sets = ",".join([f"{k}=?" for k in fields])
    params = list(fields.values()) + [item_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE items SET {sets} WHERE id=?", params)
        if tags is not None:
            conn.execute("DELETE FROM item_tags WHERE item_id=?", (item_id,))
            tag_to_id = _ensure_tags(conn, tags)
            conn.executemany(
                "INSERT OR IGNORE INTO item_tags(item_id, tag_id) VALUES (?,?)",
                [(item_id, tag_id) for tag_id in tag_to_id.values()],
            )


def set_status(item_id: int, status: ItemStatus) -> None:
    update_item(item_id, status=status)


def delete_item(item_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM items WHERE id=?", (item_id,))


def all_tags(db_path: Optional[str] = None) -> List[str]:
    with get_conn(db_path) as conn:
        cur = conn.execute("SELECT name FROM tags ORDER BY name COLLATE NOCASE")
        return [r[0] for r in cur.fetchall()]


