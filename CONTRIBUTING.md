# Contributing to Research Paper Extractor

Thank you for your interest in contributing to Research Paper Extractor! This document provides guidelines and information for contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** to your local machine
3. **Create a new branch** for your changes
4. **Make your changes** following the coding standards
5. **Test your changes** thoroughly
6. **Submit a pull request** with a clear description

## Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

3. **Run tests** (when available):
   ```bash
   python -m pytest
   ```

## Coding Standards

- **Python version**: 3.8+
- **Code style**: Follow PEP 8 guidelines
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Include type hints for function parameters and return values
- **Error handling**: Use proper exception handling
- **Logging**: Use the logging module for debug/info messages

## Project Structure

```
research_paper_extractor/
├── __init__.py          # Package initialization and exports
├── arxiv_api.py         # arXiv API interface
├── downloader.py        # Paper downloader
└── config.py            # Configuration settings

main.py                  # CLI interface
setup.py                 # Package setup
requirements.txt          # Dependencies
```

## Adding New Features

1. **Discuss the feature** by opening an issue first
2. **Implement the feature** following the existing code patterns
3. **Add tests** for new functionality
4. **Update documentation** including README and docstrings
5. **Update requirements.txt** if new dependencies are added

## Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the problem
- **Steps to reproduce**: Step-by-step instructions
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, package versions
- **Error messages**: Full error traceback if applicable

## Pull Request Guidelines

1. **Title**: Clear, descriptive title
2. **Description**: Detailed description of changes
3. **Related issues**: Link to any related issues
4. **Testing**: Describe how you tested your changes
5. **Breaking changes**: Note any breaking changes

## Code Review Process

1. **Automated checks** must pass (CI/CD when available)
2. **Code review** by maintainers
3. **Address feedback** and make requested changes
4. **Approval** from at least one maintainer
5. **Merge** when ready

## Contact

- **Author**: Sreeram
- **Email**: sreeram.lagisetty@gmail.com
- **GitHub**: [Sreeram5678](https://github.com/Sreeram5678)

## License

For licensing information, please contact Sreeram at sreeram.lagisetty@gmail.com.

---

Thank you for contributing to Research Paper Extractor! Your contributions help make this tool better for researchers worldwide.
