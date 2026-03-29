"""
Utility helpers shared across the research_paper_extractor package.

Functions:
    deduplicate_papers    — remove duplicate papers from a list
    filter_by_year        — keep only papers from a given year range
    filter_by_author      — keep only papers by a given author
    filter_by_category    — keep only papers in a given category
    sort_papers           — sort by date, title, or author
    papers_to_json        — serialize a list of papers to JSON string
    papers_from_dict      — reconstruct paper-like dicts from JSON
    truncate_text         — shorten text to N chars with ellipsis
    format_file_size      — format byte count as KB/MB/GB string
    open_url_in_browser   — open an arXiv URL in the default browser
"""

import json
import webbrowser
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from .arxiv_api import ArxivPaper

logger = logging.getLogger(__name__)


# ── Filtering ─────────────────────────────────────────────────────────────────

def deduplicate_papers(papers: List[ArxivPaper]) -> List[ArxivPaper]:
    """
    Remove duplicate papers from a list, keeping the first occurrence.

    Uses ArxivPaper.__hash__/__eq__ (arXiv ID-based) for deduplication.

    Args:
        papers: Input list (may contain duplicates)

    Returns:
        New list with duplicates removed, original order preserved
    """
    seen = set()
    result = []
    for paper in papers:
        if paper.id not in seen:
            seen.add(paper.id)
            result.append(paper)
    return result


def filter_by_year(papers: List[ArxivPaper],
                    start_year: Optional[int] = None,
                    end_year: Optional[int] = None) -> List[ArxivPaper]:
    """
    Keep only papers published within [start_year, end_year] (inclusive).

    Args:
        papers: Input list
        start_year: Minimum publication year (inclusive). None = no lower bound.
        end_year: Maximum publication year (inclusive). None = no upper bound.

    Returns:
        Filtered list
    """
    result = []
    for p in papers:
        yr = p.published.year
        if start_year is not None and yr < start_year:
            continue
        if end_year is not None and yr > end_year:
            continue
        result.append(p)
    return result


def filter_by_author(papers: List[ArxivPaper], author_name: str,
                      exact: bool = False) -> List[ArxivPaper]:
    """
    Keep only papers that have a specific author.

    Args:
        papers: Input list
        author_name: Author name to search for (case-insensitive substring)
        exact: If True, require an exact full-name match

    Returns:
        Filtered list
    """
    name_lower = author_name.lower()
    result = []
    for p in papers:
        for a in p.authors:
            if exact:
                if a.lower() == name_lower:
                    result.append(p)
                    break
            else:
                if name_lower in a.lower():
                    result.append(p)
                    break
    return result


def filter_by_category(papers: List[ArxivPaper], category: str) -> List[ArxivPaper]:
    """
    Keep only papers that belong to a given arXiv category.

    Args:
        papers: Input list
        category: arXiv category code (e.g. 'cs.LG')

    Returns:
        Filtered list
    """
    return [p for p in papers if category in p.categories]


# ── Sorting ───────────────────────────────────────────────────────────────────

_SORT_KEYS = {
    'date':    lambda p: p.published,
    'title':   lambda p: p.title.lower(),
    'author':  lambda p: p.authors[0].lower() if p.authors else '',
    'updated': lambda p: p.updated,
}


def sort_papers(papers: List[ArxivPaper],
                by: str = 'date',
                ascending: bool = False) -> List[ArxivPaper]:
    """
    Sort a list of papers.

    Args:
        papers: Input list
        by: Sort key — 'date', 'title', 'author', or 'updated'
        ascending: Sort direction (default: descending / newest first)

    Returns:
        New sorted list
    """
    if by not in _SORT_KEYS:
        raise ValueError(f"Invalid sort key '{by}'. Choose from: {list(_SORT_KEYS.keys())}")
    return sorted(papers, key=_SORT_KEYS[by], reverse=not ascending)


# ── Serialisation ─────────────────────────────────────────────────────────────

def papers_to_json(papers: List[ArxivPaper], indent: int = 2) -> str:
    """
    Serialize a list of papers to a JSON string.

    Args:
        papers: List of ArxivPaper objects
        indent: JSON indent level

    Returns:
        JSON string
    """
    return json.dumps([p.to_dict() for p in papers], indent=indent, ensure_ascii=False)


# ── Text helpers ──────────────────────────────────────────────────────────────

def truncate_text(text: str, max_chars: int = 200, suffix: str = '...') -> str:
    """
    Truncate text to at most max_chars characters.

    Args:
        text: Input string
        max_chars: Maximum character count (including suffix)
        suffix: Appended when truncation occurs

    Returns:
        Possibly truncated string
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars - len(suffix)] + suffix


def format_file_size(size_bytes: int) -> str:
    """
    Format a byte count as a human-readable size string.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted string like '1.23 MB'
    """
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if size_bytes < 1024:
            return f'{size_bytes:.1f} {unit}'
        size_bytes /= 1024
    return f'{size_bytes:.1f} PB'


# ── Browser helper ────────────────────────────────────────────────────────────

def open_url_in_browser(url: str) -> bool:
    """
    Open a URL in the system's default web browser.

    Args:
        url: URL to open

    Returns:
        True if the browser was opened successfully
    """
    try:
        webbrowser.open(url)
        logger.info(f'Opened in browser: {url}')
        return True
    except Exception as e:
        logger.error(f'Could not open browser: {e}')
        return False
