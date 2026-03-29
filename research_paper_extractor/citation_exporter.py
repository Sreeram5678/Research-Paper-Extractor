"""
Citation exporter module for exporting paper metadata in various citation formats.
Supports: BibTeX, RIS, APA, and plain text.
"""

import re
from typing import List, Optional
from datetime import datetime
from .arxiv_api import ArxivPaper


def _clean_latex(text: str) -> str:
    """Remove common LaTeX markup from text."""
    # Remove common LaTeX commands
    text = re.sub(r'\$.*?\$', '', text)  # Remove inline math
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)  # \command{text} -> text
    text = re.sub(r'\\[a-zA-Z]+', '', text)  # lone commands
    return text.strip()


def _arxiv_id_to_bibtex_key(paper: ArxivPaper) -> str:
    """Generate a BibTeX citation key from a paper."""
    first_author_last = paper.authors[0].split()[-1] if paper.authors else 'Unknown'
    # Remove non-alphanumeric chars
    first_author_last = re.sub(r'[^a-zA-Z]', '', first_author_last)
    year = paper.published.year
    # First word of title (alphanumeric only)
    first_title_word = re.sub(r'[^a-zA-Z]', '', paper.title.split()[0]) if paper.title else 'Paper'
    return f"{first_author_last}{year}{first_title_word}"


def export_bibtex(papers: List[ArxivPaper]) -> str:
    """
    Export papers as BibTeX entries.

    Args:
        papers: List of ArxivPaper objects

    Returns:
        BibTeX-formatted string
    """
    entries = []
    for paper in papers:
        key = _arxiv_id_to_bibtex_key(paper)
        authors_bibtex = ' and '.join(paper.authors)
        title = _clean_latex(paper.title)
        abstract = _clean_latex(paper.summary)[:300] + ('...' if len(paper.summary) > 300 else '')

        entry = f"""@article{{{key},
  title     = {{{title}}},
  author    = {{{authors_bibtex}}},
  journal   = {{arXiv preprint arXiv:{paper.id}}},
  year      = {{{paper.published.year}}},
  month     = {{{paper.published.strftime('%b').lower()}}},
  eprint    = {{{paper.id}}},
  archivePrefix = {{arXiv}},
  primaryClass  = {{{paper.categories[0] if paper.categories else 'cs'}}},
  url       = {{{paper.abs_url}}},
  abstract  = {{{abstract}}}
}}"""
        entries.append(entry)
    return '\n\n'.join(entries)


def export_ris(papers: List[ArxivPaper]) -> str:
    """
    Export papers in RIS format (compatible with EndNote, Zotero, Mendeley).

    Args:
        papers: List of ArxivPaper objects

    Returns:
        RIS-formatted string
    """
    entries = []
    for paper in papers:
        lines = [
            'TY  - JOUR',
            f'TI  - {_clean_latex(paper.title)}',
        ]
        for author in paper.authors:
            lines.append(f'AU  - {author}')
        lines += [
            f'PY  - {paper.published.year}',
            f'DA  - {paper.published.strftime("%Y/%m/%d")}',
            f'JO  - arXiv',
            f'VL  - {paper.id}',
            f'UR  - {paper.abs_url}',
            f'AB  - {_clean_latex(paper.summary)[:500]}',
        ]
        for cat in paper.categories:
            lines.append(f'KW  - {cat}')
        lines.append('ER  - ')
        entries.append('\n'.join(lines))
    return '\n\n'.join(entries)


def export_apa(papers: List[ArxivPaper]) -> str:
    """
    Export papers in APA 7th edition format.

    Args:
        papers: List of ArxivPaper objects

    Returns:
        APA-formatted string
    """
    entries = []
    for paper in papers:
        # Format authors: Last, F. M., & Last, F. M.
        formatted_authors = []
        for author in paper.authors:
            parts = author.strip().split()
            if len(parts) >= 2:
                last = parts[-1]
                initials = '. '.join(p[0] for p in parts[:-1]) + '.'
                formatted_authors.append(f'{last}, {initials}')
            else:
                formatted_authors.append(author)

        if len(formatted_authors) > 1:
            authors_str = ', '.join(formatted_authors[:-1]) + f', & {formatted_authors[-1]}'
        else:
            authors_str = formatted_authors[0] if formatted_authors else 'Unknown'

        year = paper.published.year
        title = _clean_latex(paper.title)
        entry = (f'{authors_str} ({year}). {title}. '
                 f'arXiv preprint arXiv:{paper.id}. {paper.abs_url}')
        entries.append(entry)
    return '\n\n'.join(entries)


def export_plain(papers: List[ArxivPaper]) -> str:
    """
    Export papers as plain text references.

    Args:
        papers: List of ArxivPaper objects

    Returns:
        Plain text formatted string
    """
    entries = []
    for i, paper in enumerate(papers, 1):
        authors_str = ', '.join(paper.authors[:5])
        if len(paper.authors) > 5:
            authors_str += f' et al.'
        entry = (
            f'[{i}] {authors_str}. '
            f'"{_clean_latex(paper.title)}". '
            f'arXiv:{paper.id} ({paper.published.strftime("%Y-%m-%d")}). '
            f'{paper.abs_url}'
        )
        entries.append(entry)
    return '\n\n'.join(entries)


EXPORT_FORMATS = {
    'bibtex': export_bibtex,
    'ris': export_ris,
    'apa': export_apa,
    'plain': export_plain,
}

FORMAT_EXTENSIONS = {
    'bibtex': '.bib',
    'ris': '.ris',
    'apa': '.txt',
    'plain': '.txt',
}


def export_citations(papers: List[ArxivPaper], fmt: str = 'bibtex') -> str:
    """
    Export papers in the specified citation format.

    Args:
        papers: List of ArxivPaper objects
        fmt: Output format ('bibtex', 'ris', 'apa', 'plain')

    Returns:
        Formatted citation string

    Raises:
        ValueError: If format is not supported
    """
    if fmt not in EXPORT_FORMATS:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(EXPORT_FORMATS.keys())}")
    return EXPORT_FORMATS[fmt](papers)
