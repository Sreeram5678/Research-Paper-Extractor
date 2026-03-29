"""
Related papers finder.
Given one paper, finds related papers based on shared title/abstract keywords.
"""

import logging
from typing import List

from .arxiv_api import ArxivAPI, ArxivPaper
from .summarizer import extract_keywords

logger = logging.getLogger(__name__)


def find_related_papers(paper: ArxivPaper,
                         max_results: int = 10,
                         top_keywords: int = 5) -> List[ArxivPaper]:
    """
    Find papers related to the given paper using keyword-based search.

    Extracts the most significant keywords from the paper's abstract,
    builds a combined query, and searches arXiv for related work.

    Args:
        paper: The seed ArxivPaper
        max_results: Max number of related papers to return
        top_keywords: Number of keywords to use for the query

    Returns:
        List of related ArxivPaper objects (excludes the original paper)
    """
    # Extract keywords from abstract
    keywords = extract_keywords(paper.summary, top_n=top_keywords)
    kw_terms = [w for w, _ in keywords]

    # Also grab first significant title words
    title_words = [w.lower() for w in paper.title.split() if len(w) > 4][:3]

    # Combine into a search query
    query_terms = list(dict.fromkeys(kw_terms + title_words))  # deduplicate, preserve order
    query = ' '.join(query_terms[:8])

    logger.info(f'Finding related papers with query: {query}')

    api = ArxivAPI()
    results = api.search(
        query=query,
        max_results=max_results + 1,  # +1 in case original paper appears
        categories=paper.categories[:1] if paper.categories else None,
    )

    # Exclude the original paper
    related = [p for p in results if p.id != paper.id]
    return related[:max_results]


def format_related_papers(seed_paper: ArxivPaper,
                           related: List[ArxivPaper]) -> str:
    """
    Format related papers output for CLI display.

    Args:
        seed_paper: The original paper
        related: List of related papers

    Returns:
        Formatted string for display
    """
    lines = [
        '=' * 65,
        f'  PAPERS RELATED TO: {seed_paper.title[:50]}',
        f'  arXiv: {seed_paper.id}',
        '=' * 65,
    ]

    if not related:
        lines.append('\nNo related papers found.')
        return '\n'.join(lines)

    for i, paper in enumerate(related, 1):
        authors_str = ', '.join(paper.authors[:2])
        if len(paper.authors) > 2:
            authors_str += f' +{len(paper.authors) - 2}'
        lines.append(f'\n{i:>2}. {paper.title}')
        lines.append(f'    {authors_str}  |  {paper.published.strftime("%Y-%m-%d")}')
        lines.append(f'    arXiv:{paper.id}  |  {paper.abs_url}')

    lines.append(f'\n{"=" * 65}')
    return '\n'.join(lines)
