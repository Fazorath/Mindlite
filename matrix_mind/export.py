from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def export_json(rows: Iterable, out_path: str) -> None:
    data = []
    for r in rows:
        data.append({k: r[k] for k in r.keys()})
    Path(out_path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_markdown(rows: Iterable, out_path: str) -> None:
    lines = ["# Matrix Mind Export\n"]
    for r in rows:
        header = f"## #{r['id']} {r['title']} [{r['type']}] ({r['status']})\n"
        meta = f"- Priority: {r['priority']}\n- Due: {r['due_date'] or '-'}\n- Tags: {r['tags']}\n- Created: {r['created_at']}\n- Updated: {r['updated_at']}\n\n"
        body = (r["body"] or "").rstrip() + "\n\n"
        lines.extend([header, meta, body])
    Path(out_path).write_text("".join(lines), encoding="utf-8")


