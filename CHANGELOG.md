# Changelog

All notable changes to Mindlite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-19

### Added
- **Core CLI functionality** with comprehensive command set
- **Zero dependencies** - uses only Python standard library
- **Command aliases** for quick access (a=add, l=list, s=show, etc.)
- **Enhanced date parsing** supporting multiple formats:
  - ISO format: 2025-10-25
  - MM/DD/YY: 10/25/25, 10/25/2025
  - DD/MM/YY: 25/10/25, 25/10/2025
  - Relative dates: +7 (7 days from now)
  - Natural language: tomorrow, today, yesterday
- **Bulk operations** for working with multiple items:
  - `bulk done` - Mark multiple items as done
  - `bulk delete` - Delete multiple items
  - `bulk tag` - Add tags to multiple items
  - `bulk start` - Start multiple items
- **Powerful filtering** with advanced options:
  - Multiple priorities, statuses, and tags
  - Date-based filters (overdue, due-today, due-this-week)
  - Search functionality
  - Time-based filters (created-since, updated-since)
- **Export functionality** supporting JSON and Markdown formats
- **ID reset** - First item always gets ID 1 when database is empty
- **Interactive help system** with command-specific help
- **Comprehensive test suite** with 100% passing tests
- **Professional documentation**:
  - Complete README with installation guide
  - Detailed USER_MANUAL.md with workflows
  - Practical EXAMPLES.md for all use cases
  - Complete TROUBLESHOOTING.md guide

### Features
- **Item types**: todo, idea, issue
- **Priorities**: low, med, high
- **Status flow**: todo → doing → done, with blocked state
- **Tags**: Flexible tagging system for organization
- **Due dates**: Multiple date format support
- **Search**: Full-text search in titles and bodies
- **Agenda**: View upcoming items with customizable timeframes

### Technical
- **SQLite database** for fast, local storage
- **Type hints** throughout the codebase
- **Comprehensive error handling**
- **Dynamic table formatting** with terminal width adaptation
- **Timezone-aware datetime** handling
- **Parameterized queries** for security

### Documentation
- **Installation guide** with multiple methods
- **Command reference** with all options
- **Workflow examples** for different use cases
- **Best practices** and productivity tips
- **Integration examples** with other tools
- **Automation scripts** and examples
- **Troubleshooting guide** with common issues and solutions

### Testing
- **Unit tests** for all core functionality
- **Integration tests** for CLI commands
- **Database tests** for CRUD operations
- **Error handling tests** for edge cases
- **Test runner** with verbose and coverage options

## [Unreleased]

### Planned Features
- **Recurring tasks** with customizable schedules
- **Reminders** and notifications
- **Contexts/Projects** for better organization
- **Templates** for common item types
- **Import/Export** from other tools (CSV, Todoist, Notion)
- **Cloud sync** for multi-device access
- **Plugin system** for custom commands
- **Web interface** for browser-based access
- **Mobile app** companion
- **API** for third-party integrations

### Future Improvements
- **Performance optimizations** for large datasets
- **Advanced filtering** with complex queries
- **Custom themes** and styling options
- **Backup and recovery** tools
- **Analytics** and reporting features
- **Team collaboration** features
- **Offline sync** capabilities

---

## Version History

- **1.0.0** - Initial release with core functionality
- **Future versions** will follow semantic versioning

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to Mindlite.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
