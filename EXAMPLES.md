# Mindlite Examples

This file contains practical examples and usage patterns for mindlite.

## Quick Start Examples

### Basic Usage
```bash
# Initialize database
mindlite init

# Add your first item
mindlite add "Learn mindlite basics"

# List all items
mindlite list

# Show item details
mindlite show 1

# Mark as done
mindlite done 1
```

### Using Aliases
```bash
# Short commands
mindlite a "Quick task"           # add
mindlite l                        # list
mindlite s 1                      # show
mindlite e 1 --priority high      # edit
mindlite del 1 -y                 # delete
mindlite ag                       # agenda
```

## Project Management Examples

### Starting a New Project
```bash
# Project overview
mindlite add "Launch new website" --type todo --priority high --due +30 --tags project,website

# Planning phase
mindlite add "Define requirements" --type todo --priority high --tags project,planning
mindlite add "Create wireframes" --type todo --priority med --tags project,design
mindlite add "Setup development environment" --type todo --priority med --tags project,devops

# Development phase
mindlite add "Implement homepage" --type todo --priority high --tags project,frontend
mindlite add "Setup database" --type todo --priority high --tags project,backend
mindlite add "Write tests" --type todo --priority med --tags project,testing

# Launch phase
mindlite add "Deploy to production" --type todo --priority high --tags project,deployment
mindlite add "Write documentation" --type todo --priority low --tags project,docs
```

### Tracking Progress
```bash
# See all project items
mindlite list --tags project

# See high priority project items
mindlite list --tags project --priority high --open

# Start working on an item
mindlite start 1

# Mark completed items
mindlite done 2
mindlite done 3

# Bulk operations
mindlite bulk done 4,5,6
mindlite bulk tag 7,8 --tags urgent
```

### Weekly Project Review
```bash
# See what's due this week
mindlite agenda --days 7

# Check project status
mindlite list --tags project --open

# See completed work
mindlite list --tags project --status done

# Export project report
mindlite export md project-report.md
```

## Daily Workflow Examples

### Morning Planning
```bash
# Check what's due today
mindlite agenda --days 1

# See current work
mindlite list --status doing

# Check high priority items
mindlite list --priority high --open
```

### Adding New Tasks
```bash
# Urgent bug fix
mindlite add "Fix login bug" --type issue --priority high --tags bug,urgent

# Meeting preparation
mindlite add "Prepare presentation" --due tomorrow --tags meeting,work

# Learning task
mindlite add "Read React documentation" --type todo --priority low --tags learning,frontend

# Idea capture
mindlite add "AI-powered testing tool" --type idea --tags research,ai,testing
```

### End of Day Review
```bash
# Mark completed items
mindlite done 1
mindlite done 2

# Block items that can't proceed
mindlite block 3

# Check tomorrow's agenda
mindlite agenda --days 1
```

## Research and Learning Examples

### Capturing Ideas
```bash
# Research ideas
mindlite add "GraphQL vs REST API" --type idea --tags research,api
mindlite add "Microservices patterns" --type idea --tags research,architecture
mindlite add "Machine learning for code review" --type idea --tags research,ai,ml

# Learning goals
mindlite add "Learn TypeScript" --type todo --priority med --tags learning,typescript
mindlite add "Study system design" --type todo --priority low --tags learning,architecture
mindlite add "Practice algorithms" --type todo --priority med --tags learning,algorithms
```

### Converting Ideas to Tasks
```bash
# Convert research idea to learning task
mindlite edit 1 --type todo --priority med --tags learning,api

# Add due date and priority
mindlite edit 2 --type todo --priority high --due +14 --tags learning,architecture

# Start working on learning
mindlite start 3
```

### Organizing Learning
```bash
# See all learning items
mindlite list --tags learning

# See research ideas
mindlite list --type idea --tags research

# See high priority learning
mindlite list --tags learning --priority high --open
```

## Bug Tracking Examples

### Reporting Issues
```bash
# Production bugs
mindlite add "Users can't login" --type issue --priority high --tags bug,production,urgent
mindlite add "Payment processing fails" --type issue --priority high --tags bug,payment,critical

# Development bugs
mindlite add "Test suite failing" --type issue --priority med --tags bug,testing
mindlite add "Memory leak in dashboard" --type issue --priority med --tags bug,performance

# Feature requests
mindlite add "Add dark mode" --type idea --priority low --tags feature,ui
mindlite add "Export data to CSV" --type idea --priority med --tags feature,export
```

### Managing Issues
```bash
# See all bugs
mindlite list --type issue

# See high priority bugs
mindlite list --type issue --priority high --open

# See production issues
mindlite list --tags production --open

# Start working on bug
mindlite start 1

# Mark bug as resolved
mindlite done 1

# Block bug waiting for external fix
mindlite block 2
```

## Team Collaboration Examples

### Shared Workflows
```bash
# Team project items
mindlite add "Code review for PR #123" --type todo --priority high --tags team,review
mindlite add "Update team documentation" --type todo --priority med --tags team,docs
mindlite add "Plan sprint retrospective" --type todo --priority med --tags team,meeting

# Cross-team coordination
mindlite add "API integration meeting" --due +3 --tags team,api,meeting
mindlite add "Design system review" --due +5 --tags team,design,review
```

### Status Updates
```bash
# See team items
mindlite list --tags team

# See team meetings
mindlite list --tags team,meeting

# Update team items
mindlite edit 1 --status doing --tags team,review,in-progress
mindlite bulk tag 2,3 --tags team,urgent
```

## Personal Productivity Examples

### Goal Setting
```bash
# Personal goals
mindlite add "Read 12 books this year" --type todo --priority med --tags personal,reading
mindlite add "Learn Spanish" --type todo --priority low --tags personal,learning,language
mindlite add "Exercise 3x per week" --type todo --priority high --tags personal,health

# Career development
mindlite add "Complete AWS certification" --type todo --priority high --tags career,certification
mindlite add "Build portfolio website" --type todo --priority med --tags career,portfolio
mindlite add "Network at tech meetup" --type todo --priority low --tags career,networking
```

### Habit Tracking
```bash
# Daily habits
mindlite add "Morning meditation" --type todo --priority high --tags personal,habit,daily
mindlite add "Write in journal" --type todo --priority med --tags personal,habit,daily
mindlite add "Review daily goals" --type todo --priority high --tags personal,habit,daily

# Weekly habits
mindlite add "Weekly meal prep" --type todo --priority med --tags personal,habit,weekly
mindlite add "Call family" --type todo --priority high --tags personal,habit,weekly
```

### Life Management
```bash
# Health and wellness
mindlite add "Annual physical exam" --type todo --priority high --due +30 --tags personal,health
mindlite add "Dentist appointment" --type todo --priority med --due +14 --tags personal,health
mindlite add "Update emergency contacts" --type todo --priority low --tags personal,admin

# Home and finance
mindlite add "File taxes" --type todo --priority high --due +60 --tags personal,finance
mindlite add "Renew car registration" --type todo --priority med --due +45 --tags personal,admin
mindlite add "Deep clean house" --type todo --priority low --tags personal,home
```

## Advanced Usage Examples

### Complex Filtering
```bash
# Multiple criteria
mindlite list --type todo,idea --status todo,doing --priority high,med --tags work,urgent

# Date-based filtering
mindlite list --due-today --priority high
mindlite list --due-this-week --tags project
mindlite list --overdue

# Search and filter
mindlite list --search "API" --type todo --open
mindlite list --search "bug" --type issue --priority high
```

### Bulk Operations
```bash
# Mark multiple items as done
mindlite bulk done 1,2,3,4,5

# Add tags to multiple items
mindlite bulk tag 1,2,3 --tags urgent,work

# Start multiple items
mindlite bulk start 1,2,3

# Delete multiple items (with confirmation)
mindlite bulk delete 1,2,3

# Delete without confirmation
mindlite bulk delete 1,2,3 -y
```

### Data Management
```bash
# Export all data
mindlite export json full-backup.json
mindlite export md full-report.md

# Export filtered data (requires custom script)
mindlite list --tags project --open | mindlite export md project-status.md

# Regular backups
mindlite export json "backup-$(date +%Y%m%d).json"
```

### Automation Scripts
```bash
#!/bin/bash
# daily-standup.sh

echo "=== Daily Standup ==="
echo "Yesterday's completed items:"
mindlite list --status done

echo -e "\nToday's planned work:"
mindlite agenda --days 1

echo -e "\nBlocked items:"
mindlite list --status blocked

echo -e "\nHigh priority items:"
mindlite list --priority high --open
```

```bash
#!/bin/bash
# weekly-review.sh

echo "=== Weekly Review ==="
echo "Items completed this week:"
mindlite list --status done

echo -e "\nOverdue items:"
mindlite list --overdue

echo -e "\nNext week's priorities:"
mindlite agenda --days 7

echo -e "\nGenerating report..."
mindlite export md "weekly-report-$(date +%Y%m%d).md"
```

## Integration Examples

### With Git
```bash
# Add items from commit messages
git log --oneline -10 | while read commit; do
    mindlite add "Review: $commit" --type todo --tags git,review
done

# Add items from branch names
git branch -r | while read branch; do
    mindlite add "Merge: $branch" --type todo --tags git,merge
done
```

### With Calendar
```bash
# Add items from calendar events
mindlite add "Team meeting" --due "2025-10-25 14:00" --tags meeting,team
mindlite add "Doctor appointment" --due "2025-10-26 10:00" --tags personal,health
```

### With Email
```bash
# Add items from email subjects
mindlite add "Follow up on proposal" --type todo --priority med --tags email,follow-up
mindlite add "Review contract" --type todo --priority high --tags email,legal
```

## Troubleshooting Examples

### Common Issues
```bash
# Database not found
mindlite init

# Permission errors
chmod 644 ~/.mindlite.db

# Command not found
python3 -m mindlite --help

# Invalid date format
mindlite add "Task" --due 2025-10-25    # Use ISO format
mindlite add "Task" --due tomorrow      # Use natural language
mindlite add "Task" --due +7            # Use relative dates
```

### Data Recovery
```bash
# Export before making changes
mindlite export json backup.json

# Restore from backup (manual process)
# See USER_MANUAL.md for detailed recovery steps
```

---

*These examples demonstrate the flexibility and power of mindlite for various use cases. Adapt them to your specific needs and workflows.*
