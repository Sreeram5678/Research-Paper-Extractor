"""
Daily digest generator.
Creates a markdown report of the latest papers in watched or specified categories.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .arxiv_api import ArxivAPI, ArxivPaper
from .summarizer import extract_keywords
from .config import ARXIV_CATEGORIES

logger = logging.getLogger(__name__)


def generate_digest(categories: Optional[List[str]] = None,
                    keywords: Optional[List[str]] = None,
                    days: int = 1,
                    max_per_query: int = 5) -> str:
    """
    Generate a markdown digest of recent papers.

    Args:
        categories: List of arXiv category codes (e.g. ['cs.AI', 'cs.LG'])
        keywords: Additional free-text keyword queries
        days: How many days back to search
        max_per_query: Max papers per query

    Returns:
        Markdown-formatted digest string
    """
    api = ArxivAPI()
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    sections: List[str] = []

    header = f'# 📰 arXiv Daily Digest — {date_str}\n\n'
    header += f'> Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}  \n'
    header += f'> Papers from the last {days} day{"s" if days != 1 else ""}.\n\n'
    sections.append(header)

    all_papers: List[ArxivPaper] = []

    if categories:
        for cat in categories:
            cat_label = ARXIV_CATEGORIES.get(cat, cat)
            papers = api.search_recent(
                query=f'cat:{cat}',
                days=days,
                max_results=max_per_query,
            )
            if papers:
                all_papers.extend(papers)
                section = _format_section(f'📂 {cat} — {cat_label}', papers)
                sections.append(section)

    if keywords:
        for kw in keywords:
            papers = api.search_recent(
                query=kw,
                days=days,
                max_results=max_per_query,
            )
            if papers:
                all_papers.extend(papers)
                section = _format_section(f'🔍 Keyword: {kw}', papers)
                sections.append(section)

    if not all_papers:
        sections.append('_No new papers found for the selected criteria._\n')
    else:
        # Add summary stats at end
        stats_section = _format_stats(all_papers)
        sections.append(stats_section)

    return '\n'.join(sections)


def _format_section(title: str, papers: List['ArxivPaper']) -> str:  # type: ignore[name-defined]
    """Format a single category/keyword section in markdown."""
    lines = [f'## {title}\n']
    for paper in papers:
        keywords = extract_keywords(paper.summary, top_n=5)
        kw_str = ', '.join(f'`{w}`' for w, _ in keywords)
        authors = ', '.join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors += f' +{len(paper.authors) - 3}'
        lines.append(f'### [{paper.title}]({paper.abs_url})\n')
        lines.append(f'**Authors:** {authors}  ')
        lines.append(f'**Published:** {paper.published.strftime("%Y-%m-%d")} | '
                     f'**arXiv:** `{paper.id}`\n')
        lines.append(f'**Keywords:** {kw_str}\n')
        # Short abstract excerpt
        excerpt = paper.summary[:250].replace('\n', ' ')
        if len(paper.summary) > 250:
            excerpt += '...'
        lines.append(f'> {excerpt}\n')
        lines.append('---\n')
    return '\n'.join(lines)


def _format_stats(papers: List[ArxivPaper]) -> str:
    """Format a brief statistics section."""
    cat_counts: dict = {}
    for p in papers:
        for cat in p.categories:
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    top_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    lines = ['## 📊 Digest Stats\n',
             f'| Metric | Value |',
             f'|--------|-------|',
             f'| Total papers | {len(papers)} |',
             f'| Unique authors | {len(set(a for p in papers for a in p.authors))} |']
    for cat, cnt in top_cats:
        lines.append(f'| {cat} | {cnt} papers |')
    return '\n'.join(lines) + '\n'


def save_digest(content: str, output_dir: Optional[str] = None) -> str:
    """
    Save the digest to a markdown file.

    Args:
        content: Digest markdown content
        output_dir: Directory to save to (default: current directory)

    Returns:
        Path to the saved file
    """
    out_dir = Path(output_dir) if output_dir else Path('.')
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    filename = f'arxiv_digest_{date_str}.md'
    filepath = out_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f'Digest saved to {filepath}')
    return str(filepath)
