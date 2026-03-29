#!/usr/bin/env python3
"""
🚀 Research Paper Extractor v2.0.0 — Modern Research Toolkit

Available Commands:
  search         Search arXiv and Semantic Scholar
  shell          NEW: Interactive persistent session
  recommend      NEW: Activity-based suggestions
  compare        NEW: Side-by-side paper analysis
  grep-pdf       NEW: Search text inside downloaded PDFs
  library        Manage local library (add/list/tag/rate/note/export)
  digest         Generate daily research digest (MD/HTML)
  analyze        Run analytics with visualizations
  summarize      Show RAKE key-point summary
  watch          Manage the keyword/author watchlist
  check-alerts   Fetch new papers for all subscriptions
  citations      Look up Semantic Scholar citation counts
  related        Find related papers for a given arXiv ID
  categories     FULL LIST of arXiv categories
  config         Manage CLI settings (Themes, URLs)
  open           Open paper in browser
"""

import click
import sys
import os
from pathlib import Path
from typing import List, Optional
import logging

from research_paper_extractor.arxiv_api import ArxivAPI, ArxivPaper
from research_paper_extractor.downloader import PaperDownloader
from research_paper_extractor.config import DEFAULT_MAX_RESULTS, ARXIV_CATEGORIES

# ── Feature imports ────────────────────────────────────────────────────────────
from research_paper_extractor.citation_exporter import (
    export_citations, EXPORT_FORMATS, FORMAT_EXTENSIONS
)
from research_paper_extractor.analytics import analyze_papers, format_analytics_report
from research_paper_extractor.summarizer import summarize_paper
from research_paper_extractor.watchlist import (
    add_keyword, remove_keyword, add_author, remove_author,
    list_watchlist, clear_watchlist, check_for_new_papers, format_watchlist_results
)
from research_paper_extractor.library import PaperLibrary
from research_paper_extractor.batch_downloader import (
    resolve_batch, create_sample_batch_file
)
from research_paper_extractor.digest import generate_digest, save_digest
from research_paper_extractor.citations import (
    get_citation_count, enrich_papers_with_citations, format_citation_table
)
from research_paper_extractor.related_papers import find_related_papers, format_related_papers
from research_paper_extractor.pdf_manager import PDFManager
from research_paper_extractor.history import SearchHistory
from research_paper_extractor.semantic_scholar import SemanticScholarAPI
from research_paper_extractor.webhooks import WebhookManager
from research_paper_extractor.comparison import PaperComparator
from research_paper_extractor.recommender import Recommender
from research_paper_extractor.shell import InteractiveShell
from research_paper_extractor.utils import themed_header, themed_print
from research_paper_extractor import config_manager
from research_paper_extractor.bibtex_parser import parse_bibtex_file, bib_entry_to_paper_obj

# Set up logging
logging.basicConfig(
    level=logging.WARNING,  # Quieter default — only show warnings+
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# CLI Root
# ══════════════════════════════════════════════════════════════════════════════

@click.group()
@click.version_option(version='2.0.0')
def cli():
    """ArXiv Paper Downloader v2.0 — Search, download, and manage research papers."""
    pass


# ══════════════════════════════════════════════════════════════════════════════
# EXISTING COMMANDS (unchanged API, minor improvements)
# ══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('query', required=True)
@click.option('--max-results', '-n', default=None, type=int,
              help=f'Maximum papers to find (default: from config)')
@click.option('--download-dir', '-d', default=None,
              help='Directory to download papers (default: from config)')
@click.option('--categories', '-c', multiple=True,
              help='arXiv categories to search in (e.g., cs.AI, cs.LG)')
@click.option('--sort-by', default='relevance',
              type=click.Choice(['relevance', 'lastUpdatedDate', 'submittedDate']),
              help='Sort results by (default: relevance)')
@click.option('--preview-only', '-p', is_flag=True,
              help='Only preview results without downloading')
@click.option('--auto-download', '-a', is_flag=True,
              help='Automatically download all found papers without confirmation')
@click.option('--recent-days', type=int, default=None,
              help='Only show papers from the last N days')
@click.option('--add-to-library', '-l', is_flag=True,
              help='Add search results to your local library')
@click.option('--manifest', '-m', is_flag=True,
              help='Save a JSON manifest file after downloading')
@click.option('--source', '-s', default='arxiv', type=click.Choice(['arxiv', 'semantic_scholar', 'both']),
              help='Search source (default: arxiv)')
def search(query: str, max_results: Optional[int], download_dir: Optional[str],
           categories: tuple, sort_by: str, preview_only: bool,
           auto_download: bool, recent_days: Optional[int], add_to_library: bool,
           manifest: bool, source: str):
    """Search and download papers from arXiv based on a query."""

    try:
        api = ArxivAPI()
        _max = max_results or config_manager.get_max_results_from_config()
        _dir = download_dir or config_manager.get_download_dir_from_config()
        downloader = PaperDownloader(_dir, topic=query)

        click.echo(f"Searching arXiv for: '{query}'")
        if categories:
            click.echo(f"Categories: {', '.join(categories)}")

        # Validate categories
        valid_categories = list(ARXIV_CATEGORIES.keys())
        invalid_cats = [cat for cat in categories if cat not in valid_categories]
        if invalid_cats:
            click.echo(f"Warning: Invalid categories: {', '.join(invalid_cats)}")
            categories = tuple(cat for cat in categories if cat in valid_categories)

        # Search
        papers = []
        themed_header(f"Searching for: {query}")
        if source in ['arxiv', 'both']:
            click.echo(f"Searching arXiv for: '{query}'")
            if recent_days:
                papers.extend(api.search_recent(query, days=recent_days, max_results=_max))
            else:
                papers.extend(api.search(
                    query=query, max_results=_max,
                    categories=list(categories) if categories else None,
                    sort_by=sort_by
                ))
        
        if source in ['semantic_scholar', 'both']:
            ss_api = SemanticScholarAPI()
            ss_papers = ss_api.search(query, max_results=_max)
            click.echo(f"Found {len(ss_papers)} papers on Semantic Scholar")
            papers.extend(ss_papers)
        
        # Log to history
        hist = SearchHistory()
        hist.add_entry(query, filters={"categories": categories, "sort_by": sort_by}, results_count=len(papers))

        if not papers:
            click.echo("No papers found matching your query.")
            return

        click.echo(downloader.get_paper_info_summary(papers))

        # Optionally add to library
        if add_to_library:
            lib = PaperLibrary()
            added = sum(1 for p in papers if lib.add_paper(p))
            click.echo(f"Added {added} new paper(s) to your library.")

        if preview_only:
            click.echo("Preview mode — no papers downloaded.")
            return

        if auto_download or click.confirm(f"\nDownload {len(papers)} papers?"):
            click.echo("\nStarting downloads...")
            downloaded_files = downloader.download_papers(papers)
            click.echo(downloader.create_download_summary(downloaded_files))
            if downloaded_files:
                click.echo("Download completed successfully!")
                if manifest:
                    mpath = downloader.save_download_manifest(papers, downloaded_files)
                    click.echo(f"Manifest saved: {mpath}")
                if add_to_library:
                    lib = PaperLibrary()
                    for p, fp in zip(papers, downloaded_files):
                        lib.set_file_path(p.id, fp)
            else:
                click.echo("No papers were downloaded.")
        else:
            click.echo("Download cancelled.")

    except Exception as e:
        logger.error(f"Error during search: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('arxiv_id', required=True)
@click.option('--download-dir', '-d', default=None,
              help='Directory to download paper (default: ./downloads)')
@click.option('--filename', '-f', default=None,
              help='Custom filename for the download (without extension)')
@click.option('--add-to-library', '-l', is_flag=True,
              help='Add paper to your local library after download')
def download_by_id(arxiv_id: str, download_dir: Optional[str],
                   filename: Optional[str], add_to_library: bool):
    """Download a specific paper by its arXiv ID."""

    try:
        api = ArxivAPI()
        _dir = download_dir or config_manager.get_download_dir_from_config()
        downloader = PaperDownloader(_dir, topic=f"paper_{arxiv_id}")

        click.echo(f"Looking up arXiv paper: {arxiv_id}")
        paper = api.get_paper_by_id(arxiv_id)
        if not paper:
            click.echo(f"Paper with ID '{arxiv_id}' not found.")
            return

        click.echo(f"\nFound paper:")
        click.echo(f"   Title: {paper.title}")
        click.echo(f"   Authors: {', '.join(paper.authors)}")
        click.echo(f"   Published: {paper.published.strftime('%Y-%m-%d')}")
        click.echo(f"   Categories: {', '.join(paper.categories)}")

        if add_to_library:
            lib = PaperLibrary()
            lib.add_paper(paper)
            click.echo("   Added to library.")

        if click.confirm(f"\nDownload this paper?"):
            click.echo("\nStarting download...")
            filepath = downloader.download_paper(paper, filename)
            if filepath:
                click.echo(f"Downloaded successfully: {filepath}")
                if add_to_library:
                    PaperLibrary().set_file_path(paper.id, filepath)
            else:
                click.echo("Download failed.")
        else:
            click.echo("Download cancelled.")

    except Exception as e:
        logger.error(f"Error downloading paper: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('author_name', required=True)
@click.option('--max-results', '-n', default=None, type=int,
              help='Maximum number of papers to find (default: from config)')
@click.option('--download-dir', '-d', default=None,
              help='Directory to download papers (default: ./downloads)')
@click.option('--preview-only', '-p', is_flag=True,
              help='Only preview results without downloading')
def search_by_author(author_name: str, max_results: Optional[int],
                     download_dir: Optional[str], preview_only: bool):
    """Search for papers by a specific author."""

    try:
        api = ArxivAPI()
        _max = max_results or config_manager.get_max_results_from_config()
        _dir = download_dir or config_manager.get_download_dir_from_config()
        downloader = PaperDownloader(_dir, topic=f"author_{author_name}")

        click.echo(f"Searching papers by author: {author_name}")
        papers = api.search_by_author(author_name, _max)

        if not papers:
            click.echo(f"No papers found for author '{author_name}'.")
            return

        click.echo(downloader.get_paper_info_summary(papers))

        if preview_only:
            click.echo("Preview mode — no papers downloaded.")
            return

        if click.confirm(f"\nDownload {len(papers)} papers?"):
            click.echo("\nStarting downloads...")
            downloaded_files = downloader.download_papers(papers)
            click.echo(downloader.create_download_summary(downloaded_files))
            if downloaded_files:
                click.echo("Download completed successfully!")
            else:
                click.echo("No papers were downloaded.")
        else:
            click.echo("Download cancelled.")

    except Exception as e:
        logger.error(f"Error searching by author: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def categories():
    """List available arXiv categories."""

    click.echo("Available arXiv categories:\n")
    for category, description in ARXIV_CATEGORIES.items():
        click.echo(f"  {category:<15} - {description}")
    click.echo(f"\nUse with --categories/-c option")
    click.echo(f"   Example: python main.py search 'machine learning' -c cs.LG -c cs.AI")


@cli.command()
@click.option('--query', '-q', prompt=True, help='Search query')
@click.option('--max-results', '-n', default=None, type=int,
              help='Maximum number of papers')
@click.option('--download-dir', '-d', default=None, help='Download directory')
def interactive(query: str, max_results: Optional[int], download_dir: Optional[str]):
    """Interactive mode for searching and downloading papers."""

    try:
        api = ArxivAPI()
        _max = max_results or config_manager.get_max_results_from_config()
        _dir = download_dir or config_manager.get_download_dir_from_config()
        downloader = PaperDownloader(_dir, topic=f"interactive_{query}")

        while True:
            click.echo(f"\nSearching for: '{query}'")
            papers = api.search(query, max_results=_max)

            if not papers:
                click.echo("No papers found.")
                if click.confirm("Try a different search?"):
                    query = click.prompt("Enter new search query")
                    downloader = PaperDownloader(_dir, topic=f"interactive_{query}")
                    continue
                break

            click.echo(f"\nFound {len(papers)} papers:")
            for i, paper in enumerate(papers, 1):
                click.echo(f"\n{i}. {paper.title}")
                click.echo(f"   Authors: {', '.join(paper.authors[:2])}")
                if len(paper.authors) > 2:
                    click.echo(f"   and {len(paper.authors) - 2} others")
                click.echo(f"   ID: {paper.id} | Published: {paper.published.strftime('%Y-%m-%d')}")

            click.echo(f"\nOptions:")
            click.echo(f"  'all' - Download all papers")
            click.echo(f"  '1,3,5' - Download specific papers by number")
            click.echo(f"  'none' - Don't download anything")
            click.echo(f"  'new' - New search")

            choice = click.prompt("What would you like to do?", default="none").strip().lower()

            if choice == "none":
                click.echo("No downloads.")
            elif choice == "all":
                downloaded_files = downloader.download_papers(papers)
                click.echo(downloader.create_download_summary(downloaded_files))
            elif choice == "new":
                query = click.prompt("Enter new search query")
                downloader = PaperDownloader(_dir, topic=f"interactive_{query}")
                continue
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in choice.split(',')]
                    selected = [papers[i] for i in indices if 0 <= i < len(papers)]
                    if selected:
                        downloaded_files = downloader.download_papers(selected)
                        click.echo(downloader.create_download_summary(downloaded_files))
                    else:
                        click.echo("Invalid paper numbers.")
                except ValueError:
                    click.echo("Invalid format. Use numbers separated by commas (e.g., '1,3,5')")

            if not click.confirm("\nContinue searching?"):
                break

        click.echo("\nGoodbye!")

    except KeyboardInterrupt:
        click.echo("\n\nGoodbye!")
    except Exception as e:
        logger.error(f"Error in interactive mode: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 1 — Citation Export
# ══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('query', required=True)
@click.option('--format', '-f', 'fmt',
              type=click.Choice(list(EXPORT_FORMATS.keys())),
              default='bibtex', show_default=True,
              help='Citation export format')
@click.option('--max-results', '-n', default=None, type=int,
              help='Max papers to include')
@click.option('--output', '-o', default=None,
              help='Output file path (default: print to stdout)')
@click.option('--categories', '-c', multiple=True,
              help='arXiv categories to filter')
def export(query: str, fmt: str, max_results: Optional[int],
           output: Optional[str], categories: tuple):
    """Export paper citations in BibTeX, RIS, APA, or plain text format.

    \b
    Examples:
      python main.py export "transformers NLP" -f bibtex -o refs.bib
      python main.py export "graph neural networks" -f apa
    """
    try:
        api = ArxivAPI()
        _max = max_results or config_manager.get_max_results_from_config()
        click.echo(f"Searching: '{query}'...")
        papers = api.search(
            query=query, max_results=_max,
            categories=list(categories) if categories else None,
        )
        if not papers:
            click.echo("No papers found.")
            return

        click.echo(f"Exporting {len(papers)} papers as {fmt.upper()}...")
        citation_text = export_citations(papers, fmt=fmt)

        if output:
            out_path = Path(output)
            ext = FORMAT_EXTENSIONS[fmt]
            if not output.endswith(ext):
                out_path = Path(output + ext)
            out_path.write_text(citation_text, encoding='utf-8')
            click.echo(f"Citations saved to: {out_path}")
        else:
            click.echo('\n' + citation_text)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 2 — Analytics
# ══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('query', required=True)
@click.option('--max-results', '-n', default=50, show_default=True,
              help='Number of papers to analyze')
@click.option('--categories', '-c', multiple=True, help='arXiv categories to filter')
@click.option('--output', '-o', default=None,
              help='Save report to this file path')
def analyze(query: str, max_results: int, categories: tuple, output: Optional[str]):
    """Run analytics on arXiv search results.

    Shows statistics on authors, categories, publication years, and keywords.

    \b
    Example:
      python main.py analyze "deep learning" -n 100
    """
    try:
        api = ArxivAPI()
        click.echo(f"Fetching {max_results} papers for analysis: '{query}'...")
        papers = api.search(
            query=query, max_results=max_results,
            categories=list(categories) if categories else None,
        )
        if not papers:
            click.echo("No papers found.")
            return

        stats = analyze_papers(papers)
        report = format_analytics_report(stats)
        click.echo(report)

        if output:
            Path(output).write_text(report, encoding='utf-8')
            click.echo(f"\nReport saved to: {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 3 — Summarize
# ══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('arxiv_id_or_query', required=True)
@click.option('--sentences', '-s', default=3, show_default=True,
              help='Number of key sentences to extract')
@click.option('--keywords', '-k', default=8, show_default=True,
              help='Number of keywords to show')
@click.option('--is-query', '-q', is_flag=True,
              help='Treat argument as a search query instead of an arXiv ID')
@click.option('--max-results', '-n', default=None, type=int,
              help='Max results when using --is-query')
def summarize(arxiv_id_or_query: str, sentences: int, keywords: int,
              is_query: bool, max_results: Optional[int]):
    """Show a TF-IDF key-point summary of paper abstract(s).

    \b
    Examples:
      python main.py summarize 2301.07041
      python main.py summarize "attention mechanism" --is-query -n 3
    """
    try:
        api = ArxivAPI()
        papers: List[ArxivPaper] = []

        if is_query:
            _max = max_results or 5
            click.echo(f"Searching: '{arxiv_id_or_query}'...")
            papers = api.search(arxiv_id_or_query, max_results=_max)
        else:
            paper = api.get_paper_by_id(arxiv_id_or_query)
            if paper:
                papers = [paper]

        if not papers:
            click.echo("No papers found.")
            return

        for paper in papers:
            click.echo('\n' + '─' * 65)
            click.echo(summarize_paper(paper, max_sentences=sentences, top_keywords=keywords))
        click.echo('─' * 65)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 4 — Watchlist management
# ══════════════════════════════════════════════════════════════════════════════

@cli.group()
def watch():
    """Manage your keyword/author watchlist for new paper alerts."""
    pass


@watch.command('add-keyword')
@click.argument('keyword', required=True)
def watch_add_keyword(keyword: str):
    """Add a keyword to your watchlist."""
    if add_keyword(keyword):
        click.echo(f"✓ Added keyword: '{keyword}'")
    else:
        click.echo(f"Keyword '{keyword}' is already in your watchlist.")


@watch.command('remove-keyword')
@click.argument('keyword', required=True)
def watch_remove_keyword(keyword: str):
    """Remove a keyword from your watchlist."""
    if remove_keyword(keyword):
        click.echo(f"✓ Removed keyword: '{keyword}'")
    else:
        click.echo(f"Keyword '{keyword}' not found in watchlist.")


@watch.command('add-author')
@click.argument('author', required=True)
def watch_add_author(author: str):
    """Add an author to your watchlist."""
    if add_author(author):
        click.echo(f"✓ Added author: '{author}'")
    else:
        click.echo(f"Author '{author}' is already in your watchlist.")


@watch.command('remove-author')
@click.argument('author', required=True)
def watch_remove_author(author: str):
    """Remove an author from your watchlist."""
    if remove_author(author):
        click.echo(f"✓ Removed author: '{author}'")
    else:
        click.echo(f"Author '{author}' not found in watchlist.")


@watch.command('list')
def watch_list():
    """Show your current watchlist."""
    data = list_watchlist()
    click.echo("\n── Watchlist ─────────────────────────────")
    if data['keywords']:
        click.echo("Keywords:")
        for kw in data['keywords']:
            click.echo(f"  • {kw}")
    else:
        click.echo("Keywords: (none)")

    if data['authors']:
        click.echo("Authors:")
        for au in data['authors']:
            click.echo(f"  • {au}")
    else:
        click.echo("Authors: (none)")

    lc = data.get('last_check')
    click.echo(f"\nLast checked: {lc[:16] if lc else 'never'}")
    click.echo("──────────────────────────────────────────")


@watch.command('clear')
@click.confirmation_option(prompt='Clear all watchlist entries?')
def watch_clear():
    """Clear all entries from your watchlist."""
    clear_watchlist()
    click.echo("Watchlist cleared.")


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 5 — Check alerts
# ══════════════════════════════════════════════════════════════════════════════

@cli.command('check-alerts')
@click.option('--days', '-d', default=7, show_default=True,
              help='Check for papers published in the last N days')
@click.option('--max-per-query', '-n', default=10, show_default=True,
              help='Max results per keyword/author')
@click.option('--download', is_flag=True,
              help='Download found papers automatically')
@click.option('--download-dir', default=None, help='Download directory')
def check_alerts(days: int, max_per_query: int, download: bool,
                 download_dir: Optional[str]):
    """Check your watchlist for new papers since last check.

    \b
    Example:
      python main.py check-alerts --days 3
    """
    try:
        wl = list_watchlist()
        if not wl['keywords'] and not wl['authors']:
            click.echo("Your watchlist is empty. Use 'watch add-keyword' to add entries.")
            return

        click.echo(f"Checking for new papers (last {days} days)...")
        results = check_for_new_papers(days=days, max_per_query=max_per_query)
        click.echo(format_watchlist_results(results))

        # Webhook Notification
        webhook_url = config_manager.get('notifications', 'webhook_url')
        if webhook_url and results:
            wm = WebhookManager(webhook_url)
            all_papers = [p for papers in results.values() for p in papers]
            click.echo("Sending webhook notification...")
            wm.send_notification("New Research Papers Alert", 
                                f"Found {len(all_papers)} new papers in your watchlist.", 
                                all_papers)

        if download and results:
            all_papers = [p for papers in results.values() for p in papers]
            if click.confirm(f"\nDownload all {len(all_papers)} found papers?"):
                _dir = download_dir or config_manager.get_download_dir_from_config()
                downloader = PaperDownloader(_dir, topic='watchlist_alerts')
                downloaded = downloader.download_papers(all_papers)
                click.echo(downloader.create_download_summary(downloaded))

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 6 — Library management
# ══════════════════════════════════════════════════════════════════════════════

@cli.group()
def library():
    """Manage your local paper library (SQLite-backed)."""
    pass


@library.command('add')
@click.argument('arxiv_id', required=True)
def library_add(arxiv_id: str):
    """Add a paper to your library by arXiv ID."""
    api = ArxivAPI()
    paper = api.get_paper_by_id(arxiv_id)
    if not paper:
        click.echo(f"Paper '{arxiv_id}' not found on arXiv.")
        return
    lib = PaperLibrary()
    if lib.add_paper(paper):
        click.echo(f"✓ Added: {paper.title[:60]}")
    else:
        click.echo("Paper is already in your library.")


@library.command('list')
@click.option('--unread', 'filter_read', flag_value=False, default=None,
              help='Show only unread papers')
@click.option('--read', 'filter_read', flag_value=True,
              help='Show only read papers')
@click.option('--tag', default=None, help='Filter by tag')
@click.option('--rating', default=None, type=int,
              help='Filter by minimum star rating (1-5)')
@click.option('--limit', '-n', default=50, show_default=True)
def library_list(filter_read, tag, rating, limit):
    """List papers in your library."""
    lib = PaperLibrary()
    papers = lib.list_papers(read=filter_read, tag=tag, rating=rating, limit=limit)
    click.echo(lib.format_library_list(papers))

    stats = lib.get_stats()
    click.echo(f"\nLibrary: {stats['total']} total | "
               f"{stats['read']} read | {stats['unread']} unread")


@library.command('mark-read')
@click.argument('arxiv_id', required=True)
@click.option('--unread', is_flag=True, help='Mark as unread instead')
def library_mark_read(arxiv_id: str, unread: bool):
    """Mark a paper as read or unread."""
    lib = PaperLibrary()
    if lib.mark_read(arxiv_id, read=not unread):
        status = 'unread' if unread else 'read'
        click.echo(f"✓ Marked {arxiv_id} as {status}.")
    else:
        click.echo(f"Paper '{arxiv_id}' not found in library.")


@library.command('rate')
@click.argument('arxiv_id', required=True)
@click.argument('rating', type=click.IntRange(1, 5))
def library_rate(arxiv_id: str, rating: int):
    """Rate a paper 1-5 stars."""
    lib = PaperLibrary()
    if lib.set_rating(arxiv_id, rating):
        click.echo(f"✓ Rated {arxiv_id}: {'★' * rating}{'☆' * (5 - rating)}")
    else:
        click.echo(f"Paper '{arxiv_id}' not found in library.")


@library.command('note')
@click.argument('arxiv_id', required=True)
@click.argument('note', required=True)
def library_note(arxiv_id: str, note: str):
    """Add or update a personal note for a paper."""
    lib = PaperLibrary()
    if lib.add_note(arxiv_id, note):
        click.echo(f"✓ Note saved for {arxiv_id}.")
    else:
        click.echo(f"Paper '{arxiv_id}' not found in library.")

@library.command('tag')
@click.argument('arxiv_id', required=True)
@click.argument('tag', required=True)
def library_tag(arxiv_id: str, tag: str):
    """Add a tag to a library paper."""
    lib = PaperLibrary()
    if lib.add_tag(arxiv_id, tag):
        click.echo(f"✓ Added tag '{tag}' to {arxiv_id}.")
    else:
        click.echo(f"Paper '{arxiv_id}' not found in library.")


@library.command('bulk-tag')
@click.argument('tag', required=True)
@click.argument('arxiv_ids', nargs=-1, required=True)
def library_bulk_tag(tag, arxiv_ids):
    """Add a tag to multiple library papers at once."""
    lib = PaperLibrary()
    count = lib.add_tags_bulk(list(arxiv_ids), tag)
    click.echo(f"✓ Added tag '{tag}' to {count} paper(s).")


@library.command('untag')
@click.argument('arxiv_id', required=True)
@click.argument('tag', required=True)
def library_untag(arxiv_id: str, tag: str):
    """Remove a tag on a library paper (alias for tag --remove)."""
    lib = PaperLibrary()
    if lib.remove_tag(arxiv_id, tag):
        click.echo(f"✓ Removed tag '{tag}' from {arxiv_id}.")
    else:
        click.echo(f"Paper '{arxiv_id}' or tag '{tag}' not found.")


@library.command('tags')
def library_tags():
    """List all unique tags in your library."""
    lib = PaperLibrary()
    tags = lib.get_all_tags()
    if not tags:
        click.echo("No tags found in your library.")
        return
    
    click.echo("\n── Library Tags ──────────────────────────")
    for t in tags:
        # Count papers with this tag
        papers = lib.list_papers(tag=t, limit=1000)
        click.echo(f"  • {t:<20} ({len(papers)} papers)")
    click.echo("──────────────────────────────────────────")


@library.command('remove')
@click.argument('arxiv_id', required=True)
@click.confirmation_option(prompt='Remove this paper from your library?')
def library_remove(arxiv_id: str):
    """Remove a paper from your library."""
    lib = PaperLibrary()
    if lib.remove_paper(arxiv_id):
        click.echo(f"✓ Removed {arxiv_id} from library.")
    else:
        click.echo(f"Paper '{arxiv_id}' not found in library.")


@library.command('stats')
def library_stats():
    """Show library statistics."""
    lib = PaperLibrary()
    stats = lib.get_stats()
    click.echo("\n── Library Statistics ────────────────────")
    click.echo(f"  Total papers : {stats['total']}")
    click.echo(f"  Read         : {stats['read']}")
    click.echo(f"  Unread       : {stats['unread']}")
    click.echo(f"  Rated papers : {stats['rated']}")
    if stats['avg_rating']:
        click.echo(f"  Avg rating   : {stats['avg_rating']:.1f} / 5.0")
    click.echo("─────────────────────────────────────────")


@library.command('export')
@click.argument('filename', required=True)
@click.option('--format', '-f', type=click.Choice(['csv', 'json', 'bibtex']), default='csv', show_default=True)
def library_export(filename, format):
    """Export the entire paper library to CSV, JSON, or BibTeX."""
    lib = PaperLibrary()
    
    # Ensure extension
    ext = format if format != 'bibtex' else 'bib'
    if not filename.endswith(f".{ext}"):
        filename += f".{ext}"
        
    click.echo(f"Exporting library to {filename} ({format.upper()})...")
    
    success = False
    if format == 'csv':
        success = lib.export_to_csv(filename)
    elif format == 'json':
        success = lib.export_to_json(filename)
    else:
        success = lib.export_to_bibtex(filename)
        
    if success:
        click.echo(f"✓ Library exported successfully to: {filename}")
    else:
        click.echo("Error: Could not export library (is it empty?)", err=True)


@library.command('export-md')
@click.argument('output_dir', type=click.Path())
@click.option('--tag', '-t', default=None, help='Filter papers by tag')
def library_export_md(output_dir: str, tag: Optional[str]):
    """Export papers to Markdown files (Obsidian/Notion compatible)."""
    from research_paper_extractor.markdown_exporter import export_library_to_markdown
    
    lib = PaperLibrary()
    papers = lib.list_papers(tag=tag, limit=10000)
    
    if not papers:
        click.echo("No papers found matching the filter.")
        return
        
    click.echo(f"Exporting {len(papers)} papers to {output_dir}...")
    count = export_library_to_markdown(papers, output_dir)
    click.echo(f"✓ successfully exported {count} papers as Markdown.")


@library.command('import-bib')
@click.argument('bib_file', type=click.Path(exists=True))
@click.option('--fetch-metadata', '-f', is_flag=True, help='Fetch full metadata from arXiv for each ID')
def library_import_bib(bib_file: str, fetch_metadata: bool):
    """Import papers from a .bib file into your library."""
    from research_paper_extractor.bibtex_parser import parse_bibtex_file, bib_entry_to_paper_obj
    
    entries = parse_bibtex_file(bib_file)
    if not entries:
        click.echo(f"No valid arXiv entries found in {bib_file}.")
        return

    click.echo(f"Found {len(entries)} candidate papers in BibTeX file.")
    lib = PaperLibrary()
    api = ArxivAPI()
    
    added_count = 0
    with click.progressbar(entries, label='Importing papers') as bar:
        for entry in bar:
            arxiv_id = entry.get('arxiv_id')
            if not arxiv_id:
                continue
                
            paper = None
            if fetch_metadata:
                try:
                    paper = api.get_paper_by_id(arxiv_id)
                except Exception:
                    pass
            
            if not paper:
                # Use metadata from BibTeX
                mock_entry = bib_entry_to_paper_obj(entry)
                if mock_entry:
                    paper = ArxivPaper(mock_entry)
            
            if paper:
                if lib.add_paper(paper):
                    added_count += 1
                
    click.echo(f"✓ Successfully imported {added_count} new papers to library.")


@library.command('sync-metadata')
@click.option('--arxiv-id', '-i', default=None, help='Sync metadata for a specific arXiv ID')
@click.option('--all', 'sync_all', is_flag=True, help='Sync metadata for all papers in library')
def library_sync_metadata(arxiv_id: Optional[str], sync_all: bool):
    """Sync citation counts and metadata for papers from Semantic Scholar."""
    from research_paper_extractor.citations import get_citation_count
    from datetime import datetime, timezone
    
    lib = PaperLibrary()
    
    if arxiv_id:
        papers_to_sync = [lib.get_paper(arxiv_id)] if lib.get_paper(arxiv_id) else []
    elif sync_all:
        papers_to_sync = lib.list_papers(limit=1000)
    else:
        click.echo("Please specify --arxiv-id or --all.")
        return
        
    if not papers_to_sync:
        click.echo("No papers found to sync.")
        return
        
    click.echo(f"Syncing {len(papers_to_sync)} papers...")
    synced_count = 0
    with click.progressbar(papers_to_sync, label='Syncing metadata') as bar:
        for p in bar:
            aid = p.get('arxiv_id')
            if not aid:
                continue
                
            citations = get_citation_count(aid)
            if citations:
                metadata = {
                    'citation_count': citations['citation_count'],
                    'last_synced': datetime.now(timezone.utc).isoformat()
                }
                if lib.update_paper_metadata(aid, metadata):
                    synced_count += 1
                    
    click.echo(f"✓ Finished syncing metadata for {synced_count} paper(s).")


@cli.command()
@click.argument('id1', required=True)
@click.argument('id2', required=True)
@click.option('--ai', is_flag=True, help='Use Gemini AI for deep comparison')
def compare(id1: str, id2: str, ai: bool):
    """Compare two papers by their arXiv IDs."""
    from research_paper_extractor.comparison import PaperComparator
    from research_paper_extractor.arxiv_api import ArxivAPI
    
    api = ArxivAPI()
    click.echo(f"Fetching metadata for {id1} and {id2}...")
    
    p1 = api.get_paper_by_id(id1)
    p2 = api.get_paper_by_id(id2)
    
    if not p1 or not p2:
        click.echo("Error: Could not fetch both papers.")
        return
        
    pc = PaperComparator()
    
    if ai:
        click.echo("Generating AI comparison report (this may take a few seconds)...")
        report = pc.ai_compare(p1, p2)
        click.echo("\n── AI COMPARISON REPORT ──────────────────")
        click.echo(report)
        click.echo("──────────────────────────────────────────")
    else:
        diff = pc.compare(p1, p2)
        click.echo(pc.format_comparison_report(p1, p2, diff))


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 7 — Batch download
# ══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('batch_file', required=True)
@click.option('--download-dir', '-d', default=None, help='Download directory')
@click.option('--max-per-query', '-n', default=5, show_default=True,
              help='Max papers per search query in the batch file')
@click.option('--preview-only', '-p', is_flag=True,
              help='Preview papers without downloading')
@click.option('--add-to-library', '-l', is_flag=True,
              help='Add resolved papers to your library')
@click.option('--create-sample', is_flag=True,
              help='Create a sample batch file at BATCH_FILE path')
def batch(batch_file: str, download_dir: Optional[str], max_per_query: int,
          preview_only: bool, add_to_library: bool, create_sample: bool):
    """Download papers listed in a .txt or .csv batch file.

    \b
    Batch file format (.txt — one entry per line):
      2301.07041          <- arXiv ID
      attention mechanism <- search query (anything not matching ID format)
      # Comments start with #

    \b
    Batch file format (.csv):
      id,2301.07041
      query,graph neural networks

    \b
    Examples:
      python main.py batch papers.txt
      python main.py batch --create-sample my_batch.txt
    """
    try:
        if create_sample:
            create_sample_batch_file(batch_file)
            click.echo(f"Sample batch file created: {batch_file}")
            return

        click.echo(f"Resolving batch file: {batch_file}")
        papers = resolve_batch(batch_file, max_results_per_query=max_per_query)

        if not papers:
            click.echo("No papers found from batch file.")
            return

        click.echo(f"\nResolved {len(papers)} papers:")
        for i, paper in enumerate(papers, 1):
            click.echo(f"  {i:>3}. [{paper.id}] {paper.title[:55]}")

        if add_to_library:
            lib = PaperLibrary()
            added = sum(1 for p in papers if lib.add_paper(p))
            click.echo(f"\nAdded {added} new paper(s) to library.")

        if preview_only:
            click.echo("\nPreview mode — no papers downloaded.")
            return

        if click.confirm(f"\nDownload all {len(papers)} papers?"):
            _dir = download_dir or config_manager.get_download_dir_from_config()
            downloader = PaperDownloader(_dir, topic='batch_download')
            downloaded = downloader.download_papers(papers)
            click.echo(downloader.create_download_summary(downloaded))

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 8 — Daily Digest
# ══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.option('--categories', '-c', multiple=True,
              help='arXiv categories (e.g. cs.AI cs.LG). Can repeat.')
@click.option('--keywords', '-k', multiple=True,
              help='Free-text keywords. Can repeat.')
@click.option('--days', '-d', default=1, show_default=True,
              help='Look-back window in days')
@click.option('--max-per-query', '-n', default=5, show_default=True,
              help='Max papers per category/keyword')
@click.option('--output-dir', '-o', default='.', show_default=True,
              help='Directory to save the digest markdown file')
@click.option('--print-only', '-p', is_flag=True,
              help='Print to stdout instead of saving to file')
@click.option('--format', '-f', type=click.Choice(['md', 'html']), default='md',
              help='Output format (default: md)')
def digest(categories: tuple, keywords: tuple, days: int,
           max_per_query: int, output_dir: str, print_only: bool, format: str):
    """Generate a daily digest of recent arXiv papers."""
    try:
        if not categories and not keywords:
            # Default to a few popular categories
            categories = ('cs.AI', 'cs.LG', 'cs.CL')
            click.echo("No categories/keywords specified — using defaults: cs.AI, cs.LG, cs.CL")

        click.echo(f"Generating digest for last {days} day(s)...")
        content = generate_digest(
            categories=list(categories) if categories else None,
            keywords=list(keywords) if keywords else None,
            days=days,
            max_per_query=max_per_query,
        )

        if print_only:
            click.echo(content)
        else:
            filepath = save_digest(content, output_dir=output_dir, format=format)
            click.echo(f"✓ Digest saved to: {filepath}")
            line_count = content.count('\n')
            click.echo(f"  ({line_count} lines, {len(content)} characters)")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 9 — Citation counts
# ══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('query_or_id', required=True)
@click.option('--is-id', '-i', is_flag=True,
              help='Treat argument as a single arXiv ID')
@click.option('--max-results', '-n', default=10, show_default=True,
              help='Max papers when treating as a search query')
def citations(query_or_id: str, is_id: bool, max_results: int):
    """Look up citation counts from Semantic Scholar.

    \b
    Examples:
      python main.py citations 2301.07041 --is-id
      python main.py citations "attention is all you need" -n 5
    """
    try:
        api = ArxivAPI()
        papers: List[ArxivPaper] = []

        if is_id:
            paper = api.get_paper_by_id(query_or_id)
            if paper:
                papers = [paper]
        else:
            click.echo(f"Searching: '{query_or_id}'...")
            papers = api.search(query_or_id, max_results=max_results)

        if not papers:
            click.echo("No papers found.")
            return

        click.echo(f"Looking up citation counts for {len(papers)} papers "
                   f"(this may take a moment)...")
        enriched = enrich_papers_with_citations(papers)
        click.echo('\n' + format_citation_table(enriched))

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 10 — Related papers
# ══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('arxiv_id', required=True)
@click.option('--max-results', '-n', default=10, show_default=True,
              help='Number of related papers to find')
@click.option('--download', '-d', is_flag=True,
              help='Download the related papers')
@click.option('--download-dir', default=None, help='Download directory')
def related(arxiv_id: str, max_results: int, download: bool,
            download_dir: Optional[str]):
    """Discover papers related to a given arXiv paper.

    Uses TF-IDF keyword extraction from the abstract to build a
    related-work search query.

    \b
    Example:
      python main.py related 2301.07041
      python main.py related 2301.07041 -n 5 --download
    """
    try:
        api = ArxivAPI()
        click.echo(f"Fetching paper: {arxiv_id}")
        paper = api.get_paper_by_id(arxiv_id)
        if not paper:
            click.echo(f"Paper '{arxiv_id}' not found.")
            return

        click.echo(f"Finding papers related to: {paper.title[:60]}")
        related_papers = find_related_papers(paper, max_results=max_results)
        click.echo(format_related_papers(paper, related_papers))

        if download and related_papers:
            if click.confirm(f"\nDownload {len(related_papers)} related papers?"):
                _dir = download_dir or config_manager.get_download_dir_from_config()
                downloader = PaperDownloader(_dir, topic=f'related_{arxiv_id}')
                downloaded = downloader.download_papers(related_papers)
                click.echo(downloader.create_download_summary(downloaded))

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 11 — Config management
# ══════════════════════════════════════════════════════════════════════════════

@cli.group()
def config():
    """View and manage user configuration settings."""
    pass


@config.command('show')
def config_show():
    """Display current configuration."""
    click.echo(config_manager.show_config())


@config.command('set')
@click.argument('section')
@click.argument('key')
@click.argument('value')
def config_set(section: str, key: str, value: str):
    """Set a configuration value.

    \b
    Examples:
      python main.py config set general max_results 20
      python main.py config set general download_dir ~/my_papers
      python main.py config set display show_abstract_preview false
    """
    config_manager.set_value(section, key, value)
    click.echo(f"✓ Set [{section}] {key} = {value}")


@config.command('theme')
@click.argument('theme_name', type=click.Choice(['cyan', 'green', 'blue', 'yellow', 'white']))
def config_theme(theme_name):
    """Set the CLI color theme."""
    config_manager.set_value('display', 'theme', theme_name)
    themed_print(f"✓ CLI theme set to: {theme_name}", "success")


@config.command('reset')
@click.confirmation_option(prompt='Reset all settings to defaults?')
def config_reset():
    """Reset all configuration to defaults."""
    config_manager.reset_config()
    click.echo("✓ Configuration reset to defaults.")


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 12 — Open paper in browser
# ══════════════════════════════════════════════════════════════════════════════

@cli.command('open')
@click.argument('arxiv_id', required=True)
@click.option('--pdf', is_flag=True, help='Open the PDF URL instead of the abstract page')
def open_paper(arxiv_id: str, pdf: bool):
    """Open an arXiv paper in your default web browser.

    \b
    Examples:
      python main.py open 1706.03762
      python main.py open 1706.03762 --pdf
    """
    from research_paper_extractor.utils import open_url_in_browser

    if pdf:
        url = f'https://arxiv.org/pdf/{arxiv_id}'
    else:
        url = f'https://arxiv.org/abs/{arxiv_id}'

    click.echo(f"Opening: {url}")
    success = open_url_in_browser(url)
    if not success:
        click.echo(f"Could not open browser. Please visit: {url}", err=True)


# ══════════════════════════════════════════════════════════════════════════════
# FEATURE 13 — Paper info (quick paper details, no download)
# ══════════════════════════════════════════════════════════════════════════════

@cli.command()
@click.argument('arxiv_id', required=True)
@click.option('--full-abstract', '-a', is_flag=True,
              help='Show full abstract instead of truncated preview')
@click.option('--summarize', '-s', 'do_summarize', is_flag=True,
              help='Show TF-IDF key-point summary of abstract')
def info(arxiv_id: str, full_abstract: bool, do_summarize: bool):
    """Display paper metadata without downloading.

    Shows title, authors, categories, abstract preview, and URLs.

    \b
    Examples:
      python main.py info 1706.03762
      python main.py info 2301.07041 --full-abstract
      python main.py info 2301.07041 --summarize
    """
    try:
        api = ArxivAPI()
        click.echo(f"Looking up: {arxiv_id}...")
        paper = api.get_paper_by_id(arxiv_id)
        if not paper:
            click.echo(f"Paper '{arxiv_id}' not found.", err=True)
            sys.exit(1)

        themed_header(paper.title)
        click.echo(f"\nAuthors     : {', '.join(paper.authors)}")
        click.echo(f"arXiv ID    : {paper.id}")
        
        # Citations
        try:
            citations = get_citation_count(paper.id)
            if citations is not None:
                click.echo(f"Citations   : {citations} (via Semantic Scholar)")
        except Exception:
            pass

        click.echo(f"Published   : {paper.published.strftime('%Y-%m-%d')}")
        click.echo(f"Updated     : {paper.updated.strftime('%Y-%m-%d')}")
        click.echo(f"Categories  : {', '.join(paper.categories)}")
        click.echo(f"Abstract URL: {paper.abs_url}")
        if paper.pdf_url:
            click.echo(f"PDF URL     : {paper.pdf_url}")

        # Check for local file
        lib = PaperLibrary()
        local_path = lib.get_file_path(arxiv_id)
        if local_path and os.path.exists(local_path):
            click.echo(f"Local Path  : {local_path}")
            pdf_meta = PDFManager.get_metadata(local_path)
            if "error" not in pdf_meta:
                click.echo(f"PDF Pages   : {pdf_meta['page_count']}")
                click.echo(f"File Size   : {pdf_meta['file_size'] / 1024 / 1024:.2f} MB")

        click.echo('\nAbstract:')
        if full_abstract:
            click.echo(paper.summary)
        else:
            from research_paper_extractor.utils import truncate_text
            click.echo(truncate_text(paper.summary, max_chars=300))

        if do_summarize:
            from research_paper_extractor.summarizer import summarize_paper
            click.echo('\n--- AI-free Summary ---')
            click.echo(summarize_paper(paper))

        click.echo('═' * 65)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)



@cli.command('pdf-info')
@click.argument('path', type=click.Path(exists=True))
def pdf_info(path):
    """Extract and display metadata directly from a PDF file."""
    click.echo(f"Extracting metadata from: {path}")
    meta = PDFManager.get_metadata(path)
    
    if "error" in meta:
        click.echo(f"Error: {meta['error']}", err=True)
        return

    click.echo('\n' + '─' * 45)
    click.echo(f"{'Property':<15} | {'Value'}")
    click.echo('─' * 45)
    for key, value in meta.items():
        if key == 'file_size':
            value = f"{value / 1024 / 1024:.2f} MB"
        click.echo(f"{key.replace('_', ' ').title():<15} | {value}")
    click.echo('─' * 45)


@cli.group('history')
def history():
    """View and manage your search history."""
    pass


@history.command('list')
@click.option('--limit', '-n', default=20, show_default=True, help='Number of entries to show')
@click.option('--clear', is_flag=True, help='Clear the search history')
def history_list(limit, clear):
    """View or clear your search history."""
    hist = SearchHistory()
    if clear:
        if click.confirm("Clear all search history?"):
            hist.clear()
            click.echo("✓ Search history cleared.")
        return

    click.echo(hist.format_history(limit))


@history.command('stats')
def history_stats():
    """Display statistics about your search patterns."""
    hist = SearchHistory()
    stats = hist.get_stats()
    
    if not stats:
        click.echo("No search history to analyze.")
        return
        
    themed_header("Search Patterns Analytics")
    themed_print(f"Total Searches  : {stats['total_searches']}", "info")
    themed_print(f"Unique Queries  : {stats['unique_queries']}", "info")
    
    click.echo("\nTop 5 Most Frequent Queries:")
    for query, count in stats['top_queries']:
        click.echo(f"  - '{query}' ({count} times)")


@cli.command('grep-pdf')
@click.argument('query', required=True)
@click.option('--path', '-p', default=None, help='File or directory to search (default: download_dir)')
@click.option('--case-sensitive', '-i', is_flag=True, help='Perform case-sensitive search')
def grep_pdf(query, path, case_sensitive):
    """Search for text inside downloaded PDF files."""
    search_path = path or config_manager.get_download_dir_from_config()
    
    if not os.path.exists(search_path):
        click.echo(f"Error: Path '{search_path}' does not exist.", err=True)
        return

    click.echo(f"Searching for '{query}' in {search_path}...")
    
    if os.path.isfile(search_path):
        results = {search_path: PDFManager.search_text(search_path, query, case_sensitive)}
    else:
        results = PDFManager.search_directory(search_path, query, case_sensitive)

    if not results:
        click.echo("No matches found.")
        return

    total_matches = sum(len(m) for m in results.values())
    click.echo(f"Found {total_matches} matches across {len(results)} file(s):\n")

    for file_path, matches in results.items():
        click.echo(f"📄 {os.path.basename(file_path)}")
        for match in matches[:5]: # Show first 5 matches per file
            click.echo(f"   [Page {match['page']}] {match['context']}")
        if len(matches) > 5:
            click.echo(f"   ... and {len(matches) - 5} more matches in this file.")
        click.echo("")


@cli.command('compare')
@click.argument('id1', required=True)
@click.argument('id2', required=True)
@click.option('--source', '-s', default='arxiv', type=click.Choice(['arxiv', 'semantic_scholar']), help='Search source (default: arxiv)')
def compare_papers(id1, id2, source):
    """Compare two papers by their arXiv or Semantic Scholar IDs."""
    api = ArxivAPI() if source == 'arxiv' else SemanticScholarAPI()
    
    click.echo(f"Fetching papers: {id1} and {id2}...")
    p1 = api.get_paper_by_id(id1)
    p2 = api.get_paper_by_id(id2)
    
    if not p1 or not p2:
        click.echo(f"Error: Could not find both papers. Check IDs and source.")
        return

    diff = PaperComparator.compare(p1, p2)
    click.echo(PaperComparator.format_comparison_report(p1, p2, diff))


@cli.command('recommend')
@click.option('--limit', '-l', default=5, type=int, help='Number of recommendations (default: 5)')
def recommend_papers(limit):
    """Get paper recommendations based on your search history and library tags."""
    rec = Recommender()
    themed_header("Paper Recommendations")
    
    click.echo("Analyzing your recent activity...")
    results = rec.get_recommendations(limit=limit)
    
    if not results:
        themed_print("No recommendations yet. Try searching for more papers or tagging your library!", "warning")
        return
        
    for i, p in enumerate(results, 1):
        themed_print(f"{i}. {p.title}", "info")
        click.echo(f"   ID: {p.id} | {p.abs_url}\n")


@cli.command('shell')
@click.pass_context
def shell_mode(ctx):
    """Start an interactive shell session."""
    shell = InteractiveShell(cli)
    shell.start()


@cli.command('categories')
@click.argument('search', required=False)
def list_categories(search):
    """List all supported arXiv categories and their descriptions."""
    themed_header("Supported arXiv Categories")
    
    table_data = []
    for code, desc in ARXIV_CATEGORIES.items():
        if not search or search.lower() in code.lower() or search.lower() in desc.lower():
            table_data.append([code, desc])
            
    from tabulate import tabulate
    click.echo(tabulate(table_data, headers=['Code', 'Description'], tablefmt='simple'))


if __name__ == '__main__':
    cli()
