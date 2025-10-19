from __future__ import annotations

import os
import tempfile

from matrix_mind import db
from matrix_mind.models import Item


def test_init_and_add_list():
    with tempfile.TemporaryDirectory() as td:
        os.environ["MIND_DB"] = os.path.join(td, "test.db")
        db.init_db()
        item_id = db.add_item(Item(id=None, type="todo", title="Test"))
        rows = db.list_items()
        assert any(r["id"] == item_id for r in rows)


