# Mindlite Troubleshooting Guide

This guide helps you resolve common issues and problems with mindlite.

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Command Issues](#command-issues)
3. [Database Issues](#database-issues)
4. [Data Issues](#data-issues)
5. [Performance Issues](#performance-issues)
6. [Integration Issues](#integration-issues)
7. [Recovery Procedures](#recovery-procedures)

## Installation Issues

### Command Not Found
**Problem**: `mindlite: command not found`

**Solutions**:
```bash
# Check if mindlite is installed
which mindlite

# Use python module syntax
python3 -m mindlite --help

# Install in development mode
pip install -e .

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Permission Denied
**Problem**: `Permission denied` when running mindlite

**Solutions**:
```bash
# Check file permissions
ls -la ~/.local/bin/mindlite

# Make executable
chmod +x ~/.local/bin/mindlite

# Use python module syntax
python3 -m mindlite --help
```

### Python Version Issues
**Problem**: `Python 3.11+ required`

**Solutions**:
```bash
# Check Python version
python3 --version

# Install Python 3.11+ if needed
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11
# Or use pyenv: pyenv install 3.11.0
```

## Command Issues

### Invalid Command
**Problem**: `mindlite: error: argument command: invalid choice`

**Solutions**:
```bash
# Check available commands
mindlite help

# Use correct command names
mindlite add "Task"  # not mindlite create "Task"
mindlite list       # not mindlite show-all

# Use aliases
mindlite a "Task"   # alias for add
mindlite l          # alias for list
```

### Invalid Arguments
**Problem**: `mindlite: error: unrecognized arguments`

**Solutions**:
```bash
# Check command help
mindlite help add
mindlite add --help

# Use correct argument names
mindlite add "Task" --priority high  # not --prior high
mindlite list --open                 # not --active

# Check argument values
mindlite add "Task" --type todo      # not --type task
mindlite add "Task" --priority high  # not --priority urgent
```

### Date Format Errors
**Problem**: `Invalid date format: X. Use YYYY-MM-DD`

**Solutions**:
```bash
# Use supported formats
mindlite add "Task" --due 2025-10-25    # ISO format
mindlite add "Task" --due 10/25/25      # MM/DD/YY
mindlite add "Task" --due 25/10/25      # DD/MM/YY
mindlite add "Task" --due tomorrow      # Natural language
mindlite add "Task" --due +7            # Relative

# Avoid invalid formats
# mindlite add "Task" --due 25-10-2025  # Wrong separator
# mindlite add "Task" --due next week   # Not supported
```

### Bulk Operation Errors
**Problem**: `Invalid IDs. Use comma-separated numbers`

**Solutions**:
```bash
# Use correct ID format
mindlite bulk done 1,2,3        # Correct
mindlite bulk done 1 2 3        # Wrong (spaces)
mindlite bulk done "1,2,3"      # Wrong (quotes)

# Check if IDs exist
mindlite list
mindlite show 1
```

## Database Issues

### Database Not Found
**Problem**: `Database not initialized`

**Solutions**:
```bash
# Initialize database
mindlite init

# Check database location
echo $MINDLITE_DB
ls -la ~/.mindlite.db

# Custom database location
MINDLITE_DB="/path/to/custom.db" mindlite init
```

### Permission Denied (Database)
**Problem**: `Permission denied` when accessing database

**Solutions**:
```bash
# Check database permissions
ls -la ~/.mindlite.db

# Fix permissions
chmod 644 ~/.mindlite.db

# Check directory permissions
ls -la ~/
chmod 755 ~/
```

### Database Locked
**Problem**: `Database is locked`

**Solutions**:
```bash
# Check for running processes
ps aux | grep mindlite

# Kill stuck processes
pkill -f mindlite

# Check database file
file ~/.mindlite.db

# Recreate database (backup first!)
mindlite export json backup.json
rm ~/.mindlite.db
mindlite init
```

### Corrupted Database
**Problem**: `Database disk image is malformed`

**Solutions**:
```bash
# Check database integrity
sqlite3 ~/.mindlite.db "PRAGMA integrity_check;"

# Export data before repair
mindlite export json backup.json

# Recreate database
rm ~/.mindlite.db
mindlite init

# Restore data (see Recovery Procedures)
```

## Data Issues

### Empty Results
**Problem**: `No items found` when items should exist

**Solutions**:
```bash
# Check if items exist
mindlite list

# Check filters
mindlite list --open
mindlite list --priority high
mindlite list --tags work

# Check database
sqlite3 ~/.mindlite.db "SELECT COUNT(*) FROM items;"
```

### Missing Items
**Problem**: Items disappear or are not found

**Solutions**:
```bash
# Check all items
mindlite list

# Check deleted items (if recently deleted)
# Items are permanently deleted, check backups

# Check database directly
sqlite3 ~/.mindlite.db "SELECT * FROM items;"
```

### Duplicate Items
**Problem**: Same item appears multiple times

**Solutions**:
```bash
# Check for duplicates
mindlite list | sort | uniq -d

# Delete duplicates manually
mindlite delete <duplicate_id>

# Use bulk delete for multiple duplicates
mindlite bulk delete <id1>,<id2>,<id3> -y
```

### Tag Issues
**Problem**: Tags not working or missing

**Solutions**:
```bash
# Check tag format
mindlite add "Task" --tags "tag1,tag2"  # Correct
mindlite add "Task" --tags "tag1 tag2"  # Wrong (spaces)

# Check existing tags
sqlite3 ~/.mindlite.db "SELECT * FROM tags;"

# Recreate tags
mindlite edit <id> --tags "new,tags"
```

## Performance Issues

### Slow Commands
**Problem**: Commands take too long to execute

**Solutions**:
```bash
# Check database size
ls -lh ~/.mindlite.db

# Clean up old items
mindlite list --status done
mindlite bulk delete <old_done_items> -y

# Optimize database
sqlite3 ~/.mindlite.db "VACUUM;"
sqlite3 ~/.mindlite.db "ANALYZE;"
```

### Memory Usage
**Problem**: High memory usage

**Solutions**:
```bash
# Check memory usage
ps aux | grep mindlite

# Use smaller filters
mindlite list --priority high  # Instead of mindlite list

# Export and restart
mindlite export json backup.json
# Restart terminal/process
```

### Large Database
**Problem**: Database file is very large

**Solutions**:
```bash
# Check database size
ls -lh ~/.mindlite.db

# Archive old items
mindlite list --status done
mindlite export json archive.json
mindlite bulk delete <old_items> -y

# Compress database
sqlite3 ~/.mindlite.db "VACUUM;"
```

## Integration Issues

### Shell Integration
**Problem**: Aliases not working

**Solutions**:
```bash
# Check shell configuration
cat ~/.bashrc | grep mindlite
cat ~/.zshrc | grep mindlite

# Add aliases
echo 'alias m="mindlite"' >> ~/.bashrc
echo 'alias ma="mindlite add"' >> ~/.bashrc
source ~/.bashrc

# Use full commands
mindlite add "Task"  # Instead of ma "Task"
```

### Script Integration
**Problem**: Scripts fail when calling mindlite

**Solutions**:
```bash
# Use full path
/usr/local/bin/mindlite add "Task"

# Use python module
python3 -m mindlite add "Task"

# Check PATH in scripts
echo $PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Export Issues
**Problem**: Export fails or creates empty files

**Solutions**:
```bash
# Check file permissions
touch test.json
ls -la test.json

# Use absolute paths
mindlite export json /full/path/to/file.json

# Check disk space
df -h

# Check if items exist
mindlite list
```

## Recovery Procedures

### Data Backup
**Before any recovery, always backup your data**:
```bash
# Export all data
mindlite export json backup-$(date +%Y%m%d).json
mindlite export md backup-$(date +%Y%m%d).md

# Copy database file
cp ~/.mindlite.db ~/.mindlite.db.backup
```

### Restore from Backup
**If you have a JSON backup**:
```bash
# Create new database
mindlite init

# Restore data (requires custom script)
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

### Database Recovery
**If database is corrupted**:
```bash
# Try to recover data
sqlite3 ~/.mindlite.db ".dump" > recovery.sql

# Create new database
rm ~/.mindlite.db
mindlite init

# Restore from dump (if possible)
sqlite3 ~/.mindlite.db < recovery.sql
```

### Complete Reset
**If all else fails**:
```bash
# Backup current state
mindlite export json last-resort-backup.json

# Remove database
rm ~/.mindlite.db

# Reinitialize
mindlite init

# Start fresh
mindlite add "Start over"
```

## Getting Help

### Built-in Help
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

### Debugging
```bash
# Verbose output
python3 -m mindlite --help

# Check database directly
sqlite3 ~/.mindlite.db "SELECT * FROM items;"
sqlite3 ~/.mindlite.db "SELECT * FROM tags;"
sqlite3 ~/.mindlite.db "SELECT * FROM item_tags;"

# Check environment
echo $MINDLITE_DB
which mindlite
python3 --version
```

### Logging
**For advanced debugging, you can add logging**:
```bash
# Add to your shell script
export PYTHONPATH="/path/to/mindlite:$PYTHONPATH"
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import mindlite.cli
mindlite.cli.main()
"
```

## Prevention Tips

### Regular Maintenance
```bash
# Weekly backup
mindlite export json "backup-$(date +%Y%m%d).json"

# Monthly cleanup
mindlite list --status done
mindlite bulk delete <old_items> -y

# Database optimization
sqlite3 ~/.mindlite.db "VACUUM;"
```

### Best Practices
- Always backup before major changes
- Use descriptive item titles
- Keep database size manageable
- Use consistent tagging
- Test commands before bulk operations

### Monitoring
```bash
# Check database health
sqlite3 ~/.mindlite.db "PRAGMA integrity_check;"

# Monitor disk usage
du -h ~/.mindlite.db

# Check for errors
mindlite list 2>&1 | grep -i error
```

---

*If you encounter issues not covered in this guide, please check the project repository for updates or create an issue with detailed information about your problem.*
