## MATRIX MIND

Matrix-style console/TUI app for capturing ideas, todos, and issues.

- Fast local storage with SQLite
- CLI (Typer) and TUI (Textual)
- Green-on-black Matrix aesthetic

## Quickstart

```bash
poetry install
poetry run mind init
poetry run mind add "Prototype Textual view" --type idea --tags ui,roadmap --priority high
poetry run mind list --open
poetry run mind board
poetry run mind-tui
```

## Status Flow
- todo → doing → blocked → done

## Environment
- DB path defaults to `~/.matrix_mind.db`, override with `MIND_DB`.

Screenshots: (placeholder)
 - TUI list view
 - TUI kanban view


