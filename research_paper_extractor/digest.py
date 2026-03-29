"""
Daily digest generator.
Creates a markdown report of the latest papers in watched or specified categories.
"""

import logging
from datetime import datetime, timezone
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
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    sections: List[str] = []

    header = f'# 📰 arXiv Daily Digest — {date_str}\n\n'
    header += f'> Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}  \n'
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


def markdown_to_html(md_content: str) -> str:
    """Very simple markdown to HTML converter (subset of MD)."""
    import re
    html = md_content
    # Headers
    html = re.sub(r'^# (.*)$', r'<h1>\1</h1>', html, flags=re.M)
    html = re.sub(r'^## (.*)$', r'<h2>\1</h2>', html, flags=re.M)
    html = re.sub(r'^### \[(.*)\]\((.*)\)$', r'<h3><a href="\2">\1</a></h3>', html, flags=re.M)
    # Quotes
    html = re.sub(r'^> (.*)$', r'<blockquote>\1</blockquote>', html, flags=re.M)
    # Bold / Code
    html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', html)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    # Horizontal Rule
    html = re.sub(r'^---$', r'<hr>', html, flags=re.M)
    # Newlines
    html = html.replace('\n', '<br>')
    
    # Wrap in basic HTML5 boilerplate
    template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>arXiv Daily Digest</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; line-height: 1.6; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }}
        h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        h2 {{ margin-top: 40px; color: #444; }}
        blockquote {{ border-left: 4px solid #ddd; padding-left: 20px; color: #666; font-style: italic; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }}
        a {{ color: #0066cc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    {html}
</body>
</html>"""
    return template


def save_digest(content: str, output_dir: Optional[str] = None, format: str = 'md') -> str:
    """
    Save the digest to a file.
    """
    out_dir = Path(output_dir) if output_dir else Path('.')
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    if format == 'html':
        filename = f'arxiv_digest_{date_str}.html'
        content = markdown_to_html(content)
    else:
        filename = f'arxiv_digest_{date_str}.md'
        
    filepath = out_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    logger.info(f'Digest saved to {filepath}')
    return str(filepath)
