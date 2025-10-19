# Contributing to Mindlite

Thank you for your interest in contributing to Mindlite! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/Project04-BattleStation.git
   cd Project04-BattleStation
   ```
3. **Install in development mode**:
   ```bash
   pip install -e .
   ```
4. **Run tests** to ensure everything works:
   ```bash
   python3 run_tests.py
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.11 or higher
- Git

### Development Installation
```bash
# Clone the repository
git clone https://github.com/Fazorath/Project04-BattleStation.git
cd Project04-BattleStation

# Install in development mode
pip install -e .

# Run tests
python3 run_tests.py --verbose
```

## 📝 Making Changes

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused

### Testing
- All new features must include tests
- Run tests before submitting: `python3 run_tests.py`
- Aim for 100% test coverage
- Test both success and failure cases

### Documentation
- Update relevant documentation files
- Add examples for new features
- Update the USER_MANUAL.md if needed
- Update EXAMPLES.md with new use cases

## 🐛 Reporting Issues

When reporting issues, please include:

1. **Python version**: `python3 --version`
2. **Operating system**: macOS, Linux, Windows
3. **Steps to reproduce**: Clear, numbered steps
4. **Expected behavior**: What should happen
5. **Actual behavior**: What actually happens
6. **Error messages**: Full error output if any

### Issue Templates
Use the provided issue templates:
- **Bug Report**: For reporting bugs
- **Feature Request**: For suggesting new features
- **Documentation**: For documentation improvements

## ✨ Feature Requests

When suggesting new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** clearly
3. **Explain the benefit** to users
4. **Consider the scope** - keep it minimal
5. **Provide examples** of how it would work

## 🔄 Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   python3 run_tests.py --verbose
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

### Pull Request Guidelines
- **Clear title**: Describe what the PR does
- **Detailed description**: Explain the changes and why
- **Link issues**: Reference any related issues
- **Screenshots**: If UI changes are involved
- **Testing**: Confirm tests pass

## 🏗️ Project Structure

```
mindlite/
├── __init__.py          # Package initialization
├── __main__.py          # Entry point for python -m mindlite
├── cli.py               # Command-line interface
├── db.py                # Database operations
├── models.py            # Data models and validation
├── utils.py             # Utility functions
└── export.py            # Export functionality

tests/
├── test_mindlite.py     # Unit tests
└── test_mindlite_cli.py # CLI integration tests

docs/
├── README.md            # Installation and quick start
├── USER_MANUAL.md       # Complete user guide
├── EXAMPLES.md          # Usage examples
└── TROUBLESHOOTING.md   # Problem solving guide
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python3 run_tests.py

# Run with verbose output
python3 run_tests.py --verbose

# Run with coverage (if coverage.py installed)
python3 run_tests.py --coverage
```

### Test Structure
- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test CLI commands end-to-end
- **Database tests**: Test database operations
- **Error handling**: Test error conditions

## 📚 Documentation

### Documentation Files
- **README.md**: Installation and quick start
- **USER_MANUAL.md**: Complete user guide
- **EXAMPLES.md**: Practical usage examples
- **TROUBLESHOOTING.md**: Problem solving guide

### Writing Documentation
- Use clear, simple language
- Provide practical examples
- Include command-line examples
- Update when adding features

## 🎯 Development Priorities

### Current Focus
- Bug fixes and stability improvements
- Performance optimizations
- Documentation improvements
- Test coverage expansion

### Future Features
- Plugin system
- Web interface
- Mobile app
- Cloud sync
- Advanced filtering

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

### Communication
- **Issues**: Use GitHub issues for bugs and features
- **Discussions**: Use GitHub discussions for questions
- **Pull Requests**: Use PRs for code changes

## 📋 Release Process

### Version Numbering
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number updated
- [ ] CHANGELOG.md updated
- [ ] Release notes prepared
- [ ] Tag created on GitHub

## 🆘 Getting Help

- **Documentation**: Check USER_MANUAL.md and EXAMPLES.md
- **Issues**: Search existing issues first
- **Discussions**: Use GitHub discussions for questions
- **Troubleshooting**: Check TROUBLESHOOTING.md

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to Mindlite! 🎉
