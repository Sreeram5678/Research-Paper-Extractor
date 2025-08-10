"""
Paper downloader module for downloading PDFs from arXiv.
"""

import os
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm
import logging

from config import (
    ARXIV_PDF_BASE_URL, 
    REQUEST_DELAY, 
    get_download_dir, 
    sanitize_filename,
    sanitize_topic_name
)
from arxiv_api import ArxivPaper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaperDownloader:
    """Downloads papers from arXiv."""
    
    def __init__(self, download_dir: Optional[str] = None, topic: Optional[str] = None):
        """
        Initialize the downloader.
        
        Args:
            download_dir: Directory to download papers to. If None, uses default.
            topic: Topic/query string to create a subfolder for. If None, uses root download dir.
        """
        base_dir = Path(download_dir) if download_dir else get_download_dir()
        
        if topic:
            # Create a subfolder based on the topic
            topic_folder = sanitize_topic_name(topic)
            self.download_dir = base_dir / topic_folder
            logger.info(f"Creating topic-specific folder: {topic_folder}")
        else:
            self.download_dir = base_dir
            
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.delay = REQUEST_DELAY
        
        logger.info(f"Download directory: {self.download_dir}")
    
    def download_paper(self, paper: ArxivPaper, custom_filename: Optional[str] = None) -> Optional[str]:
        """
        Download a single paper.
        
        Args:
            paper: ArxivPaper object to download
            custom_filename: Custom filename (without extension)
            
        Returns:
            Path to downloaded file if successful, None otherwise
        """
        
        if not paper.pdf_url:
            logger.error(f"No PDF URL found for paper {paper.id}")
            return None
        
        # Generate filename
        if custom_filename:
            filename = sanitize_filename(f"{custom_filename}.pdf")
        else:
            # Use paper title and ID
            title_clean = sanitize_filename(paper.title)
            filename = f"{title_clean}_{paper.id}.pdf"
        
        filepath = self.download_dir / filename
        
        # Check if file already exists
        if filepath.exists():
            logger.info(f"File already exists: {filename}")
            return str(filepath)
        
        try:
            logger.info(f"Downloading: {paper.title}")
            logger.info(f"URL: {paper.pdf_url}")
            
            # Add delay to be respectful to servers
            time.sleep(self.delay)
            
            # Download with progress bar
            self._download_with_progress(paper.pdf_url, filepath)
            
            logger.info(f"Downloaded: {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error downloading {paper.id}: {e}")
            # Clean up partial download
            if filepath.exists():
                filepath.unlink()
            return None
    
    def download_papers(self, 
                       papers: List[ArxivPaper], 
                       max_downloads: Optional[int] = None) -> List[str]:
        """
        Download multiple papers.
        
        Args:
            papers: List of ArxivPaper objects to download
            max_downloads: Maximum number of papers to download
            
        Returns:
            List of paths to successfully downloaded files
        """
        
        if max_downloads:
            papers = papers[:max_downloads]
        
        downloaded_files = []
        
        logger.info(f"Starting download of {len(papers)} papers...")
        
        for i, paper in enumerate(papers, 1):
            logger.info(f"Downloading paper {i}/{len(papers)}")
            
            filepath = self.download_paper(paper)
            if filepath:
                downloaded_files.append(filepath)
            
            # Progress update
            print(f"Progress: {i}/{len(papers)} papers processed")
        
        logger.info(f"Download complete. {len(downloaded_files)} papers downloaded successfully.")
        return downloaded_files
    
    def _download_with_progress(self, url: str, filepath: Path):
        """
        Download a file with a progress bar.
        
        Args:
            url: URL to download from
            filepath: Path to save the file
        """
        
        try:
            # Create request with headers to mimic a browser
            request = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; arXiv-downloader/1.0)'
                }
            )
            
            with urllib.request.urlopen(request) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                
                with open(filepath, 'wb') as f:
                    if total_size > 0:
                        with tqdm(total=total_size, unit='B', unit_scale=True, desc=filepath.name) as pbar:
                            while True:
                                chunk = response.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                                pbar.update(len(chunk))
                    else:
                        # No content length, just download
                        f.write(response.read())
                        
        except urllib.error.HTTPError as e:
            if e.code == 403:
                logger.error(f"Access forbidden for {url}. Paper may not be available.")
            else:
                logger.error(f"HTTP error {e.code} for {url}: {e.reason}")
            raise
        except urllib.error.URLError as e:
            logger.error(f"URL error for {url}: {e.reason}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading {url}: {e}")
            raise
    
    def get_paper_info_summary(self, papers: List[ArxivPaper]) -> str:
        """
        Generate a summary of papers to be downloaded.
        
        Args:
            papers: List of papers
            
        Returns:
            Formatted summary string
        """
        
        if not papers:
            return "No papers found."
        
        summary = f"\nFound {len(papers)} papers:\n"
        summary += "=" * 50 + "\n"
        
        for i, paper in enumerate(papers, 1):
            summary += f"{i}. {paper.title}\n"
            summary += f"   Authors: {', '.join(paper.authors[:3])}"
            if len(paper.authors) > 3:
                summary += f" and {len(paper.authors) - 3} others"
            summary += f"\n   arXiv ID: {paper.id}\n"
            summary += f"   Published: {paper.published.strftime('%Y-%m-%d')}\n"
            summary += f"   Categories: {', '.join(paper.categories)}\n"
            summary += "-" * 50 + "\n"
        
        return summary
    
    def create_download_summary(self, downloaded_files: List[str]) -> str:
        """
        Create a summary of downloaded files.
        
        Args:
            downloaded_files: List of file paths that were downloaded
            
        Returns:
            Summary string
        """
        
        if not downloaded_files:
            return "No files were downloaded."
        
        summary = f"\nSuccessfully downloaded {len(downloaded_files)} papers:\n"
        summary += "=" * 50 + "\n"
        
        for i, filepath in enumerate(downloaded_files, 1):
            filename = Path(filepath).name
            file_size = Path(filepath).stat().st_size / (1024 * 1024)  # MB
            summary += f"{i}. {filename} ({file_size:.1f} MB)\n"
        
        summary += f"\nAll files saved to: {self.download_dir}\n"
        return summary
