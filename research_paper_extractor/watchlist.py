"""
Watchlist module — persist keyword/author subscriptions and check for new papers.
Stored as a JSON file in the user's home directory.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Optional, Any

from .arxiv_api import ArxivAPI, ArxivPaper

logger = logging.getLogger(__name__)

WATCHLIST_FILE = Path.home() / '.arxiv_watchlist.json'
DEFAULT_LOOKBACK_DAYS = 7


def _load_watchlist() -> Dict[str, Any]:
    """Load watchlist from disk. Returns empty structure if file doesn't exist."""
    if WATCHLIST_FILE.exists():
        try:
            with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f'Could not read watchlist file: {e}')
    return {'keywords': [], 'authors': [], 'last_check': None}


def _save_watchlist(data: Dict[str, Any]) -> None:
    """Persist watchlist to disk."""
    try:
        with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        logger.error(f'Could not save watchlist: {e}')


def add_keyword(keyword: str) -> bool:
    """
    Add a keyword to the watchlist.

    Args:
        keyword: Search keyword to watch

    Returns:
        True if added, False if already present
    """
    data = _load_watchlist()
    keyword = keyword.strip().lower()
    if keyword in data['keywords']:
        return False
    data['keywords'].append(keyword)
    _save_watchlist(data)
    return True


def remove_keyword(keyword: str) -> bool:
    """Remove a keyword from the watchlist."""
    data = _load_watchlist()
    keyword = keyword.strip().lower()
    if keyword not in data['keywords']:
        return False
    data['keywords'].remove(keyword)
    _save_watchlist(data)
    return True


def add_author(author: str) -> bool:
    """Add an author name to the watchlist."""
    data = _load_watchlist()
    author = author.strip()
    if author in data['authors']:
        return False
    data['authors'].append(author)
    _save_watchlist(data)
    return True


def remove_author(author: str) -> bool:
    """Remove an author from the watchlist."""
    data = _load_watchlist()
    if author not in data['authors']:
        return False
    data['authors'].remove(author)
    _save_watchlist(data)
    return True


def list_watchlist() -> Dict[str, List[str]]:
    """Return the current watchlist (keywords and authors)."""
    data = _load_watchlist()
    return {
        'keywords': data.get('keywords', []),
        'authors': data.get('authors', []),
        'last_check': data.get('last_check'),
    }


def clear_watchlist() -> None:
    """Clear all entries from the watchlist."""
    _save_watchlist({'keywords': [], 'authors': [], 'last_check': None})


def check_for_new_papers(days: int = DEFAULT_LOOKBACK_DAYS,
                          max_per_query: int = 10) -> Dict[str, List[ArxivPaper]]:
    """
    Check arXiv for new papers matching watchlist keywords/authors.

    Args:
        days: How many days back to look
        max_per_query: Max results per keyword/author query

    Returns:
        Dict mapping keyword/author -> list of new ArxivPaper objects
    """
    data = _load_watchlist()
    api = ArxivAPI()
    results: Dict[str, List[ArxivPaper]] = {}
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    for keyword in data.get('keywords', []):
        papers = api.search_recent(keyword, days=days, max_results=max_per_query)
        if papers:
            results[f'keyword:{keyword}'] = papers

    for author in data.get('authors', []):
        papers = api.search_by_author(author, max_results=max_per_query)
        new_papers = [p for p in papers if p.published >= cutoff]
        if new_papers:
            results[f'author:{author}'] = new_papers

    # Update last check timestamp
    data['last_check'] = datetime.now(timezone.utc).isoformat()
    _save_watchlist(data)

    return results


def format_watchlist_results(results: Dict[str, List[ArxivPaper]]) -> str:
    """Format watchlist check results for display."""
    if not results:
        return 'No new papers found for your watchlist.'

    lines = ['=' * 60, '  NEW PAPERS FROM YOUR WATCHLIST', '=' * 60]
    total = 0
    for query, papers in results.items():
        query_type, query_value = query.split(':', 1)
        label = f'Keyword: {query_value}' if query_type == 'keyword' else f'Author: {query_value}'
        lines.append(f'\n### {label} ({len(papers)} new paper{"s" if len(papers) != 1 else ""})')
        for paper in papers:
            lines.append(f'  - {paper.title}')
            lines.append(f'    arXiv:{paper.id} | {paper.published.strftime("%Y-%m-%d")}')
            lines.append(f'    {paper.abs_url}')
        total += len(papers)

    lines.append(f'\n{"=" * 60}')
    lines.append(f'Total new papers: {total}')
    return '\n'.join(lines)
