"""
Semantic Scholar API integration for citation count lookup.
Uses the free Semantic Scholar API (no key required for basic usage).
"""

import json
import logging
import time
import urllib.request
import urllib.error
from typing import Optional, Dict, List

from .arxiv_api import ArxivPaper

logger = logging.getLogger(__name__)

SS_API_BASE = 'https://api.semanticscholar.org/graph/v1'
FIELDS = 'citationCount,influentialCitationCount,year,referenceCount,publicationTypes'
REQUEST_DELAY = 1.0  # seconds, to respect rate limits


def _fetch_json(url: str) -> Optional[dict]:
    """Fetch JSON from a URL. Returns None on failure."""
    try:
        time.sleep(REQUEST_DELAY)
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'arXiv-paper-extractor/1.0 (research tool)',
                'Accept': 'application/json',
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            logger.warning('Semantic Scholar rate limit hit. Waiting 10s...')
            time.sleep(10)
        elif e.code == 404:
            logger.debug(f'Paper not found on Semantic Scholar: {url}')
        else:
            logger.warning(f'HTTP {e.code} from Semantic Scholar: {e.reason}')
        return None
    except Exception as e:
        logger.warning(f'Semantic Scholar request failed: {e}')
        return None


def get_citation_count(arxiv_id: str) -> Optional[Dict]:
    """
    Look up citation metadata for an arXiv paper via Semantic Scholar.

    Args:
        arxiv_id: arXiv ID (e.g. '2301.07041')

    Returns:
        Dict with keys: citationCount, influentialCitationCount,
                        referenceCount, year, publicationTypes
        or None if not found.
    """
    # Strip version suffix (v1, v2, ...)
    clean_id = arxiv_id.split('v')[0]
    url = f'{SS_API_BASE}/paper/arXiv:{clean_id}?fields={FIELDS}'
    data = _fetch_json(url)
    if data and 'citationCount' in data:
        return {
            'citation_count': data.get('citationCount', 0),
            'influential_citation_count': data.get('influentialCitationCount', 0),
            'reference_count': data.get('referenceCount', 0),
            'year': data.get('year'),
            'publication_types': data.get('publicationTypes', []),
        }
    return None


def enrich_papers_with_citations(papers: List[ArxivPaper]) -> List[Dict]:
    """
    Enrich a list of papers with citation counts from Semantic Scholar.

    Args:
        papers: List of ArxivPaper objects

    Returns:
        List of dicts combining ArxivPaper.to_dict() with citation data
    """
    enriched = []
    total = len(papers)
    for i, paper in enumerate(papers, 1):
        logger.info(f'Fetching citations {i}/{total}: {paper.id}')
        paper_dict = paper.to_dict()
        citations = get_citation_count(paper.id)
        if citations:
            paper_dict.update(citations)
        else:
            paper_dict['citation_count'] = None
            paper_dict['influential_citation_count'] = None
        enriched.append(paper_dict)
    return enriched


def format_citation_table(enriched_papers: List[Dict]) -> str:
    """
    Format enriched papers into a citation count table.

    Args:
        enriched_papers: Output from enrich_papers_with_citations()

    Returns:
        Formatted table string
    """
    lines = [
        '=' * 75,
        f'  {"TITLE":<40} {"ID":<15} {"CITATIONS":>9} {"INFLUENTIAL":>11}',
        '=' * 75,
    ]
    for p in enriched_papers:
        title = (p.get('title', '')[:38] + '..') if len(p.get('title', '')) > 40 else p.get('title', '')[:40]
        arxiv_id = p.get('id', 'N/A')[:14]
        cites = str(p.get('citation_count', 'N/A'))
        influential = str(p.get('influential_citation_count', 'N/A'))
        lines.append(f'  {title:<40} {arxiv_id:<15} {cites:>9} {influential:>11}')
    lines.append('=' * 75)
    return '\n'.join(lines)
