# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of Research Paper Extractor
- Command-line interface for searching and downloading arXiv papers
- Support for searching by keywords, topics, and phrases
- Author-based search functionality
- Category filtering for arXiv categories
- Recent papers search (last N days)
- Batch download capabilities
- Specific paper download by arXiv ID
- Preview mode for search results
- Interactive mode for guided searching
- Automatic topic-based folder organization
- Smart file naming and sanitization
- Progress bars for downloads
- Comprehensive error handling and logging
- Configuration file for customizable settings

### Features
- **Smart Search**: Search papers by keywords, topics, or phrases
- **Author Search**: Find all papers by specific researchers
- **Category Filtering**: Filter by arXiv categories (AI, ML, Computer Vision, etc.)
- **Recent Papers**: Find papers published in the last N days
- **Batch Download**: Download multiple papers at once
- **Specific Downloads**: Download papers by arXiv ID
- **Preview Mode**: See search results before downloading
- **Interactive Mode**: User-friendly interactive interface
- **Auto-Organization**: Automatic topic-based folder creation and file naming
- **Topic Folders**: Each search creates its own organized folder

### Technical Details
- Built with Python 3.8+
- Uses arXiv's public API
- Respectful rate limiting for server requests
- Cross-platform compatibility
- Proper package structure and setup
- Comprehensive documentation

### Dependencies
- requests >= 2.31.0
- feedparser >= 6.0.10
- beautifulsoup4 >= 4.12.2
- lxml >= 4.9.3
- tqdm >= 4.66.1
- click >= 8.1.7
- python-dateutil >= 2.8.2

---

## [2.0.0] - 2026-03-29

### Added
- **Modular Architecture**: Reorganized into a collection of specialized modules.
- **Library Management**: Persistent local paper tracking via SQLite (`library.py`).
- **Citation Export**: Bulk export to BibTeX, RIS, and APA formats (`citation_exporter.py`).
- **Research Analytics**: Rich statistical reports on author trends and keywords (`analytics.py`).
- **Watchlists**: Automated alerts for new papers from favorite authors or topics (`watchlist.py`).
- **Paper Summaries**: TF-IDF based abstract analysis and keypoint extraction (`summarizer.py`).
- **Daily Digests**: Automated markdown digests of new research (`digest.py`).
- **Discovery**: Find related papers via keyword relevance analysis (`related_papers.py`).
- **Advanced Config**: INI-based user preferences management (`config_manager.py`).
- **Batch Processing**: Download papers from text/CSV lists (`batch_downloader.py`).
- **External lookups**: Semantic Scholar integration for citation counts (`citations.py`).

### Improvements
- Refactored `__init__.py` for better package discovery.
- Cleaned up redundant instructions and metadata files from repository.
- Improved documentation with comprehensive usage examples.
