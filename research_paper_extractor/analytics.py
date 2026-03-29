"""
Analytics module for analyzing paper collections.
Provides statistics on authors, categories, publication trends, and title keywords.
"""

import re
from collections import Counter
from typing import List, Dict, Any
from .arxiv_api import ArxivPaper

# Common English stop words to filter from keyword analysis
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'over', 'after',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
    'its', 'it', 'this', 'that', 'these', 'those', 'we', 'our', 'via',
    'using', 'based', 'new', 'case', 'study', 'method', 'approach',
}


def _extract_keywords(text: str, top_n: int = 20) -> List[tuple]:
    """Extract top keyword tokens from text."""
    # Lowercase, split into tokens, filter
    tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    filtered = [t for t in tokens if t not in STOP_WORDS]
    return Counter(filtered).most_common(top_n)


def analyze_papers(papers: List[ArxivPaper]) -> Dict[str, Any]:
    """
    Analyze a list of papers and return a rich statistics dictionary.

    Args:
        papers: List of ArxivPaper objects

    Returns:
        Dictionary with keys:
          - total: int
          - papers_by_year: Counter of year -> count
          - top_authors: list of (author, count) tuples
          - top_categories: list of (category, count) tuples
          - title_keywords: list of (word, count) tuples
          - abstract_keywords: list of (word, count) tuples
          - avg_authors_per_paper: float
          - most_prolific_author: str
    """
    if not papers:
        return {'total': 0}

    # --- Papers by year ---
    papers_by_year: Counter = Counter()
    for p in papers:
        papers_by_year[p.published.year] += 1

    # --- Authors ---
    author_counter: Counter = Counter()
    total_authors = 0
    for p in papers:
        for author in p.authors:
            author_counter[author] += 1
        total_authors += len(p.authors)

    # --- Categories ---
    cat_counter: Counter = Counter()
    for p in papers:
        for cat in p.categories:
            cat_counter[cat] += 1

    # --- Title keyword analysis ---
    all_titles = ' '.join(p.title for p in papers)
    title_keywords = _extract_keywords(all_titles, top_n=20)

    # --- Abstract keyword analysis ---
    all_abstracts = ' '.join(p.summary for p in papers)
    abstract_keywords = _extract_keywords(all_abstracts, top_n=20)

    # --- Collaboration size distribution ---
    collaboration_sizes = Counter()
    for p in papers:
        n = len(p.authors)
        if n == 1:
            collaboration_sizes['solo (1)'] += 1
        elif n <= 3:
            collaboration_sizes['small (2-3)'] += 1
        elif n <= 6:
            collaboration_sizes['medium (4-6)'] += 1
        else:
            collaboration_sizes['large (7+)'] += 1

    return {
        'total': len(papers),
        'papers_by_year': dict(sorted(papers_by_year.items())),
        'top_authors': author_counter.most_common(10),
        'top_categories': cat_counter.most_common(10),
        'title_keywords': title_keywords,
        'abstract_keywords': abstract_keywords,
        'avg_authors_per_paper': round(total_authors / len(papers), 2),
        'most_prolific_author': author_counter.most_common(1)[0][0] if author_counter else 'N/A',
        'collaboration_sizes': dict(collaboration_sizes),
    }


def _create_bar_chart(data: Dict[str, Any], title: str, width: int = 40) -> List[str]:
    """Create a simple ASCII bar chart."""
    if not data:
        return []
    lines = [f"\n--- {title} ---"]
    max_val = max(data.values()) if data.values() else 1
    for key, count in data.items():
        bar_len = int(count * width / max_val)
        bar = '█' * bar_len
        lines.append(f'  {str(key):<20} {bar} {count}')
    return lines


def format_analytics_report(stats: Dict[str, Any]) -> str:
    """
    Format an analytics stats dict into a human-readable text report.
    """
    if stats.get('total', 0) == 0:
        return 'No papers to analyze.'

    lines = []
    lines.append('=' * 60)
    lines.append('           PAPER ANALYTICS REPORT')
    lines.append('=' * 60)
    lines.append(f"\nTotal papers analyzed : {stats['total']}")
    lines.append(f"Avg authors per paper : {stats.get('avg_authors_per_paper', 'N/A')}")
    lines.append(f"Most prolific author  : {stats.get('most_prolific_author', 'N/A')}")

    # Visual Charts
    lines.extend(_create_bar_chart(stats.get('papers_by_year', {}), 'Papers by Year'))
    
    top_cats = {cat: count for cat, count in stats.get('top_categories', [])}
    lines.extend(_create_bar_chart(top_cats, 'Top Categories'))
    
    lines.extend(_create_bar_chart(stats.get('collaboration_sizes', {}), 'Collaboration Size'))

    lines.append('\n--- Top 10 Authors ---')
    for i, (author, count) in enumerate(stats.get('top_authors', []), 1):
        lines.append(f'  {i:>2}. {author} ({count} paper{"s" if count > 1 else ""})')

    lines.append('\n--- Top Title Keywords ---')
    kws = [f'{w}({c})' for w, c in stats.get('title_keywords', [])]
    lines.append('  ' + ', '.join(kws))

    lines.append('\n--- Top Abstract Keywords ---')
    kws = [f'{w}({c})' for w, c in stats.get('abstract_keywords', [])]
    lines.append('  ' + ', '.join(kws))

    lines.append('\n' + '=' * 60)
    return '\n'.join(lines)
