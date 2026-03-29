# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-29

### Added
- **Multi-Source API Support**: Integrated Semantic Scholar alongside arXiv for broader search coverage.
- **Interactive Shell Mode**: Added a persistent CLI shell for multi-command research sessions.
- **Bibliometric Visualizations**: Added ASCII bar charts for category, year, and collaboration analytics.
- **Paper Comparison Engine**: Side-by-side similarity analysis of paper titles, authors, and keywords.
- **Recommendation Engine**: Personalized paper suggestions based on local library tags and search history.
- **PDF Text Search**: Implemented `grep-pdf` to search inside downloaded PDF content.
- **Duplicate Discovery**: Added `library cleanup` CLI command to find and remove duplicate papers in your local library.
- **Library Exporting**: Added support for exporting the local library to BibTeX, CSV, and JSON formats.
- **CLI Theming System**: Added 5 color themes (Cyan, Green, Blue, Yellow, White) for better terminal aesthetics.
- **Webhooks**: Integrated Discord and Slack notifications for watchlist alerts.
- **RAKE Keyword Analysis**: Implemented Rapid Automatic Keyword Extraction for more accurate summaries.
- **HTML Digest Export**: Added support for generating styled HTML daily research reports.
- **Citations lookup**: Integrated citation counts in the `info` command via Semantic Scholar.
- **Expanded Categories**: Added many more sub-fields in math, finance, and economics.

### Changed
- Modernized CLI output with themed headers and formatted tables.
- Improved error handling for network requests and PDF parsing.
- Enhanced search history with pattern analytics.
- Updated README and Usage Examples for version 2.0.0.

## [1.0.0] - 2024-01-01
- Initial release with basic arXiv search and download.
