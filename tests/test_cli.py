from __future__ import annotations

import os
import tempfile

from typer.testing import CliRunner

from matrix_mind.cli import app


def test_cli_init_add_list():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as td:
        os.environ["MIND_DB"] = os.path.join(td, "cli.db")
        result = runner.invoke(app, ["init"])  # init
        assert result.exit_code == 0
        result = runner.invoke(app, [
            "add", "Hello", "--type", "todo", "--tags", "x,y", "--priority", "high"
        ])
        assert result.exit_code == 0
        result = runner.invoke(app, ["list", "--open"])  # list open
        assert result.exit_code == 0


