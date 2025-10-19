# Mindlite User Manual

## Table of Contents
1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Command Reference](#command-reference)
4. [Workflow Examples](#workflow-examples)
5. [Best Practices](#best-practices)
6. [Advanced Usage](#advanced-usage)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation
```bash
# Clone and install
git clone https://github.com/yourusername/mindlite.git
cd mindlite
pip install -e .

# Or run directly
python3 -m mindlite --help
```

### First Steps
1. **Initialize your database**: `mindlite init`
2. **Add your first item**: `mindlite add "Learn mindlite" --type todo`
3. **List your items**: `mindlite list`
4. **Get help**: `mindlite help` or `mindlite help <command>`

## Core Concepts

### Item Types
- **todo**: Tasks that need to be completed
- **idea**: Ideas, concepts, or potential projects  
- **issue**: Problems or bugs that need attention

### Priorities
- **high**: Urgent and important - do first
- **med**: Normal priority - default
- **low**: Can be done when time permits

### Status Flow
```
todo → doing → done
  ↓      ↓
blocked ←→ blocked
```

### Tags
Use tags to categorize and filter items:
- **Project tags**: `project`, `website`, `mobile-app`
- **Context tags**: `work`, `personal`, `learning`
- **Priority tags**: `urgent`, `important`, `someday`
- **Type tags**: `bug`, `feature`, `research`

## Command Reference

### Core Commands

#### `add` - Create New Items
```bash
mindlite add "Title" [options]
```

**Options:**
- `--type {todo,idea,issue}` - Item type (default: todo)
- `--body TEXT` - Description/notes
- `--priority {low,med,high}` - Priority (default: med)
- `--tags TEXT` - Comma-separated tags
- `--due DATE` - Due date (multiple formats)

**Examples:**
```bash
# Basic task
mindlite add "Fix login bug" --type issue --priority high

# With tags and due date
mindlite add "Weekly review" --due +7 --tags recurring,review

# Research idea
mindlite add "AI-powered testing" --type idea --tags research,ai,testing
```

#### `list` - Display Items
```bash
mindlite list [options]
```

**Filtering Options:**
- `--type TYPE` - Filter by type (comma-separated)
- `--status STATUS` - Filter by status (comma-separated)
- `--priority PRIORITY` - Filter by priority (comma-separated)
- `--tags TAGS` - Filter by tags (comma-separated)
- `--search TEXT` - Search in title and body
- `--open` - Show only non-done items
- `--overdue` - Show overdue items
- `--due-today` - Show items due today
- `--due-this-week` - Show items due this week
- `--due-in DAYS` - Show items due within N days

**Examples:**
```bash
# High priority open items
mindlite list --priority high --open

# Items due this week
mindlite list --due-this-week

# Search for project-related items
mindlite list --search "project"

# Multiple filters
mindlite list --type todo,idea --status todo,doing --tags urgent
```

#### `show` - Item Details
```bash
mindlite show ID
```

**Example:**
```bash
mindlite show 1
# Output:
#1 Fix login bug
#================
#Type: issue
#Status: todo
#Priority: high
#Due: Not set
#Tags: bug, urgent
#Created: 2025-10-19T12:00:00Z
#Updated: 2025-10-19T12:00:00Z
#
#Body:
#Users can't log in with valid credentials
```

#### `edit` - Modify Items
```bash
mindlite edit ID [options]
```

**Options:**
- `--title TEXT` - New title
- `--body TEXT` - New body/notes
- `--type {todo,idea,issue}` - New type
- `--status {todo,doing,blocked,done}` - New status
- `--priority {low,med,high}` - New priority
- `--due DATE` - New due date
- `--tags TAGS` - New tags (comma-separated)

**Examples:**
```bash
# Update priority
mindlite edit 1 --priority high

# Change status and add tags
mindlite edit 2 --status doing --tags urgent

# Update due date and notes
mindlite edit 3 --due tomorrow --body "Updated requirements"
```

### Status Commands

#### `start` - Begin Working
```bash
mindlite start ID
# Equivalent to: mindlite edit ID --status doing
```

#### `block` - Block Item
```bash
mindlite block ID
# Equivalent to: mindlite edit ID --status blocked
```

#### `done` - Complete Item
```bash
mindlite done ID
# Equivalent to: mindlite edit ID --status done
```

### Bulk Operations

#### `bulk` - Multiple Items
```bash
mindlite bulk ACTION IDS [options]
```

**Actions:**
- `done` - Mark items as done
- `delete` - Delete items
- `tag` - Add tags to items
- `start` - Start working on items

**Examples:**
```bash
# Mark multiple items as done
mindlite bulk done 1,2,3

# Delete multiple items (with confirmation)
mindlite bulk delete 1,2,3

# Skip confirmation for delete
mindlite bulk delete 1,2,3 -y

# Add tags to multiple items
mindlite bulk tag 1,2 --tags urgent,work

# Start multiple items
mindlite bulk start 1,2,3
```

### Utility Commands

#### `agenda` - Upcoming Items
```bash
mindlite agenda [--days DAYS]
```

**Examples:**
```bash
# Next 7 days (default)
mindlite agenda

# Next 14 days
mindlite agenda --days 14
```

#### `export` - Backup Data
```bash
mindlite export FORMAT OUTPUT
```

**Formats:**
- `json` - Machine-readable format
- `md` - Human-readable Markdown

**Examples:**
```bash
# JSON backup
mindlite export json backup.json

# Markdown report
mindlite export md weekly-report.md
```

#### `delete` - Remove Items
```bash
mindlite delete ID [-y]
```

**Examples:**
```bash
# With confirmation
mindlite delete 1

# Skip confirmation
mindlite delete 1 -y
```

## Workflow Examples

### Daily Planning
```bash
# Morning: Check what's due today
mindlite agenda --days 1

# See current work
mindlite list --status doing

# Add new urgent items
mindlite add "Fix production bug" --type issue --priority high --tags urgent,production
```

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

### Research and Ideas
```bash
# Capture ideas
mindlite add "AI-powered code review" --type idea --tags ai,research
mindlite add "Microservices architecture" --type idea --tags architecture,tech

# Convert ideas to tasks
mindlite edit 1 --type todo --priority med --tags learning,tech
mindlite edit 2 --type todo --priority low --tags learning,architecture

# Organize by tags
mindlite list --tags research
mindlite list --tags learning --open
```

### Weekly Review
```bash
# See what was completed
mindlite list --status done

# Check overdue items
mindlite list --overdue

# Plan next week
mindlite list --open --priority high
mindlite agenda --days 7

# Export for reporting
mindlite export md weekly-report.md
```

## Best Practices

### Naming Conventions
- **Be specific**: "Fix login bug" vs "Fix bug"
- **Use action verbs**: "Review", "Implement", "Test"
- **Include context**: "Review PR #123" vs "Review"

### Tagging Strategy
- **Consistent naming**: Use lowercase, hyphenated tags
- **Hierarchical tags**: `project:website`, `project:mobile`
- **Context tags**: `work`, `personal`, `learning`
- **Status tags**: `urgent`, `important`, `someday`

### Priority Guidelines
- **High**: Must be done today/this week
- **Med**: Should be done this week/month
- **Low**: Can be done when time permits

### Date Management
- **Use relative dates**: `+7` for "next week"
- **Set realistic deadlines**: Don't overcommit
- **Review regularly**: Check `--overdue` items

### Workflow Tips
- **Start small**: Begin with basic todo management
- **Use aliases**: `alias m="mindlite"` for shorter commands
- **Regular backups**: Export data weekly
- **Clean up**: Delete completed items regularly

## Advanced Usage

### Command Aliases
Create shell aliases for even shorter commands:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias m="mindlite"
alias ma="mindlite add"
alias ml="mindlite list"
alias ms="mindlite show"
alias me="mindlite edit"
alias md="mindlite done"
alias mdel="mindlite delete"
alias mag="mindlite agenda"
alias mexp="mindlite export"
```

### Environment Configuration
```bash
# Custom database location
export MINDLITE_DB="/path/to/custom.db"

# Use in scripts
MINDLITE_DB="/tmp/test.db" mindlite init
```

### Integration with Other Tools
```bash
# Add items from other tools
echo "Fix bug in production" | xargs mindlite add --type issue --priority high

# Export for other tools
mindlite export json | jq '.[] | select(.status == "done")'

# Generate reports
mindlite export md | pandoc -o report.pdf
```

### Automation Scripts
```bash
#!/bin/bash
# daily-review.sh

echo "=== Daily Review ==="
echo "Items due today:"
mindlite agenda --days 1

echo -e "\nOverdue items:"
mindlite list --overdue

echo -e "\nHigh priority open items:"
mindlite list --priority high --open
```

## Troubleshooting

### Common Issues

**Database not found**
```bash
# Solution: Initialize database
mindlite init
```

**Permission errors**
```bash
# Check database file permissions
ls -la ~/.mindlite.db
chmod 644 ~/.mindlite.db
```

**Command not found**
```bash
# Check if mindlite is in PATH
which mindlite
# Or use python module syntax
python3 -m mindlite --help
```

**Invalid date format**
```bash
# Use supported formats
mindlite add "Task" --due 2025-10-25    # ISO format
mindlite add "Task" --due 10/25/25      # MM/DD/YY
mindlite add "Task" --due tomorrow      # Natural language
mindlite add "Task" --due +7            # Relative
```

**Empty results**
```bash
# Check if items exist
mindlite list

# Check filters
mindlite list --open
mindlite list --priority high
```

### Getting Help
```bash
# General help
mindlite help

# Command-specific help
mindlite help add
mindlite help list
mindlite help bulk

# Standard argparse help
mindlite add --help
mindlite list --help
```

### Data Recovery
```bash
# Export current data
mindlite export json backup.json

# Restore from backup (manual process)
# 1. Create new database
mindlite init

# 2. Import data (requires custom script)
python3 -c "
import json
import sqlite3
from mindlite.db import get_conn, insert_item
from mindlite.models import Item

with open('backup.json') as f:
    data = json.load(f)

with get_conn() as conn:
    for item_data in data:
        item = Item(
            id=None,
            type=item_data['type'],
            title=item_data['title'],
            body=item_data.get('body', ''),
            status=item_data['status'],
            priority=item_data['priority'],
            due_date=item_data.get('due_date'),
            tags=item_data.get('tags', [])
        )
        insert_item(conn, item)
"
```

### Performance Tips
- **Regular cleanup**: Delete old completed items
- **Efficient filtering**: Use specific filters instead of broad searches
- **Database location**: Keep database on fast storage (SSD)
- **Backup strategy**: Export regularly, keep multiple backups

---

*This manual covers the core functionality of mindlite. For the latest updates and examples, visit the project repository.*
