# Mindlite

A minimal, stdlib-only CLI for ideas, todos, and issues.

## What it is

Mindlite is a fast, reliable command-line tool for managing your ideas, todos, and issues. It uses only Python standard library components - no external dependencies required.

## Features

- **Simple data model**: Items with type (todo/idea/issue), status, priority, due dates, and tags
- **Fast SQLite storage**: Local database at `~/.mindlite.db`
- **Clean CLI interface**: Intuitive commands with helpful output
- **Export capabilities**: JSON and Markdown export formats
- **Zero dependencies**: Uses only Python standard library

## Installation & Usage

Mindlite requires Python 3.11+. No installation needed - just run it as a module:

```bash
# Initialize the database
python -m mindlite init

# Add a new item
python -m mindlite add "Ship session draft" --type todo --priority high --tags "dnd,writing" --due 2025-10-25

# List open items
python -m mindlite list --open

# Start working on an item
python -m mindlite start 1

# Show agenda for next 7 days
python -m mindlite agenda --days 7

# Export to Markdown
python -m mindlite export md export.md
```

## Commands

### `init`
Initialize the database (idempotent).

### `add "Title" [options]`
Add a new item with optional:
- `--type {todo,idea,issue}` (default: todo)
- `--body "notes"` 
- `--priority {low,med,high}` (default: med)
- `--tags "a,b,c"`
- `--due YYYY-MM-DD`

### `list [filters]`
List items with optional filters:
- `--type {todo,idea,issue}`
- `--status {todo,doing,blocked,done}`
- `--open` (exclude done items)
- `--tag "tagname"`
- `--search "text"`
- `--due-in DAYS`

### `show ID`
Show detailed view of a single item.

### `edit ID [options]`
Edit an item with any combination of the add options.

### `start ID`, `block ID`, `done ID`
Change item status.

### `delete ID [-y]`
Delete an item (use `-y` to skip confirmation).

### `agenda [--days N]`
Show items due within N days (default: 7).

### `export {json,md} OUTPUT`
Export all items to JSON or Markdown format.

## Environment

Override the default database location:
```bash
MINDLITE_DB=/path/to/custom.db python -m mindlite list
```

## Examples

```bash
# Quick workflow
python -m mindlite init
python -m mindlite add "Review PR #123" --type todo --priority high --tags "work,review"
python -m mindlite add "Brainstorm new feature" --type idea --tags "product,innovation"
python -m mindlite list --open
python -m mindlite start 1
python -m mindlite agenda
python -m mindlite export md weekly-report.md
```

## Data Model

Items have the following fields:
- `id`: Auto-incrementing primary key
- `type`: todo, idea, or issue
- `title`: Required title
- `body`: Optional notes/description
- `status`: todo → doing → blocked → done
- `priority`: low, med, or high
- `due_date`: Optional date in YYYY-MM-DD format
- `tags`: Many-to-many relationship with tag names
- `created_at`, `updated_at`: Automatic timestamps

## Future Features (TODO)

The codebase includes hooks for future enhancements:
- Recurring tasks and reminders
- Lightweight encryption for sensitive notes
- Import from Markdown/CSV files
- Simple "contexts" (work/school/dnd) as saved filters
- Web interface
- Mobile sync
