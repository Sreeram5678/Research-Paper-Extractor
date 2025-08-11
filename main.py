#!/usr/bin/env python3
"""
ArXiv Paper Downloader - Main CLI interface
"""

import click
import sys
from typing import List, Optional
import logging

from research_paper_extractor.arxiv_api import ArxivAPI, ArxivPaper
from research_paper_extractor.downloader import PaperDownloader
from research_paper_extractor.config import DEFAULT_MAX_RESULTS, ARXIV_CATEGORIES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """ArXiv Paper Downloader - Automatically download research papers from arXiv."""
    pass

@cli.command()
@click.argument('query', required=True)
@click.option('--max-results', '-n', default=DEFAULT_MAX_RESULTS, 
              help=f'Maximum number of papers to find (default: {DEFAULT_MAX_RESULTS})')
@click.option('--download-dir', '-d', default=None,
              help='Directory to download papers (default: ./downloads)')
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
def search(query: str, max_results: int, download_dir: Optional[str], 
          categories: tuple, sort_by: str, preview_only: bool, 
          auto_download: bool, recent_days: Optional[int]):
    """Search and download papers from arXiv based on a query."""
    
    try:
        # Initialize API and downloader
        api = ArxivAPI()
        downloader = PaperDownloader(download_dir, topic=query)
        
        click.echo(f"Searching arXiv for: '{query}'")
        if categories:
            click.echo(f"Categories: {', '.join(categories)}")
        
        # Validate categories
        valid_categories = list(ARXIV_CATEGORIES.keys())
        invalid_cats = [cat for cat in categories if cat not in valid_categories]
        if invalid_cats:
            click.echo(f"Warning: Invalid categories: {', '.join(invalid_cats)}")
            categories = [cat for cat in categories if cat in valid_categories]
        
        # Search for papers
        if recent_days:
            papers = api.search_recent(query, days=recent_days, max_results=max_results)
            click.echo(f"Filtering for papers from last {recent_days} days")
        else:
            papers = api.search(
                query=query,
                max_results=max_results,
                categories=list(categories) if categories else None,
                sort_by=sort_by
            )
        
        if not papers:
            click.echo("No papers found matching your query.")
            return
        
        # Show results summary
        summary = downloader.get_paper_info_summary(papers)
        click.echo(summary)
        
        if preview_only:
            click.echo("Preview mode - no papers downloaded.")
            return
        
        # Download papers
        if auto_download or click.confirm(f"\nDownload {len(papers)} papers?"):
            click.echo("\nStarting downloads...")
            downloaded_files = downloader.download_papers(papers)
            
            # Show download summary
            download_summary = downloader.create_download_summary(downloaded_files)
            click.echo(download_summary)
            
            if downloaded_files:
                click.echo("Download completed successfully!")
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
def download_by_id(arxiv_id: str, download_dir: Optional[str], filename: Optional[str]):
    """Download a specific paper by its arXiv ID."""
    
    try:
        api = ArxivAPI()
        # Use the arxiv_id as topic for single paper downloads
        downloader = PaperDownloader(download_dir, topic=f"paper_{arxiv_id}")
        
        click.echo(f"Looking up arXiv paper: {arxiv_id}")
        
        paper = api.get_paper_by_id(arxiv_id)
        if not paper:
            click.echo(f"Paper with ID '{arxiv_id}' not found.")
            return
        
        # Show paper info
        click.echo(f"\nFound paper:")
        click.echo(f"   Title: {paper.title}")
        click.echo(f"   Authors: {', '.join(paper.authors)}")
        click.echo(f"   Published: {paper.published.strftime('%Y-%m-%d')}")
        click.echo(f"   Categories: {', '.join(paper.categories)}")
        
        if click.confirm(f"\nDownload this paper?"):
            click.echo("\nStarting download...")
            filepath = downloader.download_paper(paper, filename)
            
            if filepath:
                click.echo(f"Downloaded successfully: {filepath}")
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
@click.option('--max-results', '-n', default=DEFAULT_MAX_RESULTS,
              help=f'Maximum number of papers to find (default: {DEFAULT_MAX_RESULTS})')
@click.option('--download-dir', '-d', default=None,
              help='Directory to download papers (default: ./downloads)')
@click.option('--preview-only', '-p', is_flag=True,
              help='Only preview results without downloading')
def search_by_author(author_name: str, max_results: int, download_dir: Optional[str], preview_only: bool):
    """Search for papers by a specific author."""
    
    try:
        api = ArxivAPI()
        # Use author name as topic for author-based searches
        downloader = PaperDownloader(download_dir, topic=f"author_{author_name}")
        
        click.echo(f"Searching papers by author: {author_name}")
        
        papers = api.search_by_author(author_name, max_results)
        
        if not papers:
            click.echo(f"No papers found for author '{author_name}'.")
            return
        
        # Show results
        summary = downloader.get_paper_info_summary(papers)
        click.echo(summary)
        
        if preview_only:
            click.echo("Preview mode - no papers downloaded.")
            return
        
        if click.confirm(f"\nDownload {len(papers)} papers?"):
            click.echo("\nStarting downloads...")
            downloaded_files = downloader.download_papers(papers)
            
            download_summary = downloader.create_download_summary(downloaded_files)
            click.echo(download_summary)
            
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
    
    click.echo(f"\nUse these categories with the --categories/-c option")
    click.echo(f"   Example: python main.py search 'machine learning' -c cs.LG -c cs.AI")

@cli.command()
@click.option('--query', '-q', prompt=True, help='Search query')
@click.option('--max-results', '-n', default=DEFAULT_MAX_RESULTS,
              help=f'Maximum number of papers (default: {DEFAULT_MAX_RESULTS})')
@click.option('--download-dir', '-d', default=None,
              help='Download directory (default: ./downloads)')
def interactive(query: str, max_results: int, download_dir: Optional[str]):
    """Interactive mode for searching and downloading papers."""
    
    try:
        api = ArxivAPI()
        # Use the initial query as topic for interactive mode
        downloader = PaperDownloader(download_dir, topic=f"interactive_{query}")
        
        while True:
            click.echo(f"\nSearching for: '{query}'")
            
            # Search papers
            papers = api.search(query, max_results=max_results)
            
            if not papers:
                click.echo("No papers found.")
                if click.confirm("Try a different search?"):
                    query = click.prompt("Enter new search query")
                    # Create a new downloader for the new query
                    downloader = PaperDownloader(download_dir, topic=f"interactive_{query}")
                    continue
                break
            
            # Show papers with numbers
            click.echo(f"\nFound {len(papers)} papers:")
            for i, paper in enumerate(papers, 1):
                click.echo(f"\n{i}. {paper.title}")
                click.echo(f"   Authors: {', '.join(paper.authors[:2])}")
                if len(paper.authors) > 2:
                    click.echo(f"   and {len(paper.authors) - 2} others")
                click.echo(f"   ID: {paper.id} | Published: {paper.published.strftime('%Y-%m-%d')}")
            
            # Ask what to do
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
                summary = downloader.create_download_summary(downloaded_files)
                click.echo(summary)
            elif choice == "new":
                query = click.prompt("Enter new search query")
                # Create a new downloader for the new query
                downloader = PaperDownloader(download_dir, topic=f"interactive_{query}")
                continue
            else:
                # Parse specific paper numbers
                try:
                    indices = [int(x.strip()) - 1 for x in choice.split(',')]
                    selected_papers = [papers[i] for i in indices if 0 <= i < len(papers)]
                    
                    if selected_papers:
                        downloaded_files = downloader.download_papers(selected_papers)
                        summary = downloader.create_download_summary(downloaded_files)
                        click.echo(summary)
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

if __name__ == '__main__':
    cli()
