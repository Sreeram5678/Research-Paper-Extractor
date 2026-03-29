"""
research_paper_extractor — ArXiv paper search, download, and management toolkit.

Modules:
    arxiv_api          — ArXiv Atom feed API client
    downloader         — PDF downloader with progress bars and retry logic
    config             — Package-level constants and category definitions
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
    utils              — Shared helpers: filtering, sorting, dedup, serialisation
"""

from .arxiv_api import ArxivAPI, ArxivPaper
from .downloader import PaperDownloader
from .config import DEFAULT_MAX_RESULTS, ARXIV_CATEGORIES
from .utils import (
    deduplicate_papers,
    filter_by_year,
    filter_by_author,
    filter_by_category,
    sort_papers,
    papers_to_json,
    truncate_text,
    format_file_size,
)

__version__ = '2.1.0'
__author__ = 'Research Paper Extractor Contributors'

__all__ = [
    'ArxivAPI',
    'ArxivPaper',
    'PaperDownloader',
    'DEFAULT_MAX_RESULTS',
    'ARXIV_CATEGORIES',
    'deduplicate_papers',
    'filter_by_year',
    'filter_by_author',
    'filter_by_category',
    'sort_papers',
    'papers_to_json',
    'truncate_text',
    'format_file_size',
]
