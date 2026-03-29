"""
research_paper_extractor — ArXiv paper search, download, and management toolkit.

Modules:
    arxiv_api          — ArXiv Atom feed API client
    downloader         — PDF downloader with progress bars
    config             — Package-level constants and helpers
    citation_exporter  — BibTeX / RIS / APA / plain-text citation export
    analytics          — Statistics and analytics for paper collections
    summarizer         — TF-IDF abstract keyword extraction and summarisation
    watchlist          — Persistent keyword/author watch alerts
    library            — SQLite-backed local paper library
    config_manager     — User-level INI config file management
    batch_downloader   — Batch download from .txt / .csv files
    digest             — Markdown daily digest generator
    citations          — Semantic Scholar citation count lookup
    related_papers     — Related paper discovery via keyword search
"""

from .arxiv_api import ArxivAPI, ArxivPaper
from .downloader import PaperDownloader
from .config import DEFAULT_MAX_RESULTS, ARXIV_CATEGORIES

__version__ = '2.0.0'
__author__ = 'Research Paper Extractor Contributors'

__all__ = [
    'ArxivAPI',
    'ArxivPaper',
    'PaperDownloader',
    'DEFAULT_MAX_RESULTS',
    'ARXIV_CATEGORIES',
]
