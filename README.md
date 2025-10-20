# Mindlite

![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)
![Dependencies](https://img.shields.io/badge/dependencies-none-lightgrey.svg)

A minimal, fast CLI for managing ideas, todos, and issues using only Python's standard library.

## ✨ Features

- **Zero Dependencies**: Uses only Python standard library
- **Fast & Lightweight**: SQLite database with minimal overhead
- **Command Aliases**: Short commands for quick access (`a` = add, `l` = list, etc.)
- **Enhanced Date Parsing**: Multiple formats (MM/DD/YY, tomorrow, +7, etc.)
- **Bulk Operations**: Work with multiple items at once
- **Powerful Filtering**: Filter by priority, status, tags, dates, and more
- **Export Support**: JSON and Markdown export
- **ID Reset**: Clean starts with ID 1 when database is empty
- **Curses TUI**: Beautiful terminal interface with sidebar navigation and reader pane

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/mindlite.git
cd mindlite

# Install in development mode
pip install -e .

# Or run directly
python3 -m mindlite --help
```

### Basic Usage

```bash
# Initialize database
mindlite init

# Add items
mindlite add "Complete project proposal" --type todo --priority high --due tomorrow
mindlite add "Research new framework" --type idea --tags research,tech

# List items
mindlite list
mindlite list --priority high --open
mindlite list --tags research

# Work with items
mindlite start 1
mindlite done 1
mindlite edit 2 --priority high --tags urgent

# Bulk operations
mindlite bulk done 1,2,3
mindlite bulk tag 1,2 --tags urgent,work

# Export data
mindlite export json backup.json
mindlite export md report.md
```

## 🖥️ Terminal UI

Mindlite includes a beautiful curses-based terminal interface:

```bash
# Launch the TUI
mindlite ui

# Or use the alias
mindlite ui
```

### TUI Features

- **Sidebar Navigation**: Browse items in a vertical list
- **Reader Pane**: View item details with wrapped text
- **Status Cycling**: Press `s` to cycle through statuses
- **Smooth Scrolling**: Navigate with arrow keys or `j`/`k`
- **Responsive**: Adapts to terminal resizing
- **Color Support**: Cyan highlights and borders (with fallbacks)

### TUI Controls

| Key | Action |
|-----|--------|
| `j` / `↓` | Move down |
| `k` / `↑` | Move up |
| `Space` / `PgDn` | Page down in reader |
| `PgUp` | Page up in reader |
| `g` | Go to top of reader |
| `G` | Go to bottom of reader |
| `s` | Cycle item status |
| `r` | Refresh data |
| `q` / `Esc` | Quit |

## 📋 Command Reference

### Core Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `init` | - | Initialize database |
| `add` | `a` | Add new item |
| `list` | `l` | List items with filters |
| `show` | `s` | Show item details |
| `edit` | `e` | Edit item |
| `delete` | `del` | Delete item |
| `agenda` | `ag` | Show upcoming items |
| `export` | `exp` | Export data |
| `ui` | `ui` | Launch terminal UI |
| `help` | `h` | Show help |

### Status Commands

| Command | Description |
|---------|-------------|
| `start` | Mark item as "doing" |
| `block` | Mark item as "blocked" |
| `done` | Mark item as "done" |

### Bulk Operations

| Command | Description |
|---------|-------------|
| `bulk done <ids>` | Mark multiple items as done |
| `bulk delete <ids>` | Delete multiple items |
| `bulk tag <ids> --tags <tags>` | Add tags to multiple items |
| `bulk start <ids>` | Start multiple items |

## 🎯 Item Types

- **todo**: Tasks that need to be completed
- **idea**: Ideas, concepts, or potential projects
- **issue**: Problems or bugs that need attention

## 📊 Priorities

- **high**: Urgent and important
- **med**: Normal priority (default)
- **low**: Can be done when time permits

## 🔄 Status Flow

```
todo → doing → done
  ↓      ↓
blocked ←→ blocked
```

## 📅 Date Formats

Mindlite supports multiple date formats:

- **ISO**: `2025-10-25`
- **MM/DD/YY**: `10/25/25`, `10/25/2025`
- **DD/MM/YY**: `25/10/25`, `25/10/2025`
- **Relative**: `+7` (7 days from now)
- **Natural**: `tomorrow`, `today`, `yesterday`

## 🔍 Filtering Options

### List Command Filters

```bash
# Filter by type
mindlite list --type todo,idea

# Filter by status
mindlite list --status todo,doing

# Filter by priority
mindlite list --priority high,med

# Filter by tags
mindlite list --tags urgent,work

# Date-based filters
mindlite list --overdue
mindlite list --due-today
mindlite list --due-this-week
mindlite list --due-in 7

# Search
mindlite list --search "project"

# Time-based filters
mindlite list --created-since 2025-01-01
mindlite list --updated-since 2025-01-01

# Open items only
mindlite list --open
```

## 📁 Data Storage

- **Default location**: `~/.mindlite.db`
- **Custom location**: Set `MINDLITE_DB` environment variable
- **Backup**: Use `export` commands to create backups

## 🔧 Configuration

### Environment Variables

- `MINDLITE_DB`: Custom database path

### Command Aliases

You can create shell aliases for even shorter commands:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias m="mindlite"
alias ma="mindlite add"
alias ml="mindlite list"
alias ms="mindlite show"
```

## 📖 Examples

### Project Management

```bash
# Start a new project
mindlite add "Launch new website" --type todo --priority high --due +30 --tags project,website

# Add project tasks
mindlite add "Design homepage" --type todo --priority high --tags project,design
mindlite add "Setup CI/CD" --type todo --priority med --tags project,devops
mindlite add "Write documentation" --type todo --priority low --tags project,docs

# Track progress
mindlite list --tags project --open
mindlite start 1  # Start working on homepage
mindlite bulk tag 2,3 --tags urgent  # Mark CI/CD and docs as urgent
```

### Daily Workflow

```bash
# Morning planning
mindlite agenda --days 1  # See what's due today
mindlite list --status doing  # See current work

# Add new items throughout the day
mindlite add "Fix login bug" --type issue --priority high --tags bug,urgent
mindlite add "Team meeting notes" --type idea --tags meeting,notes

# End of day review
mindlite list --open --priority high
mindlite done 5  # Mark completed items
```

### Research and Ideas

```bash
# Capture ideas
mindlite add "AI-powered code review" --type idea --tags ai,research
mindlite add "Microservices architecture" --type idea --tags architecture,tech

# Research tasks
mindlite add "Study GraphQL" --type todo --priority med --tags learning,tech
mindlite add "Read React docs" --type todo --priority low --tags learning,frontend

# Organize by tags
mindlite list --tags research
mindlite list --tags learning --open
```

## 🚨 Troubleshooting

### Common Issues

**Database not found**
```bash
mindlite init  # Initialize database
```

**Permission errors**
```bash
# Check database file permissions
ls -la ~/.mindlite.db
chmod 644 ~/.mindlite.db
```

**Command not found**
```bash
# Make sure mindlite is in PATH
which mindlite
# Or use python module syntax
python3 -m mindlite --help
```

### Getting Help

```bash
mindlite help           # General help
mindlite add --help     # Command-specific help
mindlite list --help    # List command options
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with Python standard library
- Inspired by simple, effective CLI tools
- Database design influenced by modern task management systems
