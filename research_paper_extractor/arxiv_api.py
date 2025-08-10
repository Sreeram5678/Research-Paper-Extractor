"""
arXiv API interface for searching and retrieving paper information.
"""

import time
import urllib.parse
import urllib.request
import feedparser
from datetime import datetime
from typing import List, Dict, Optional
import logging

from config import (
    ARXIV_BASE_URL, 
    REQUEST_DELAY, 
    DEFAULT_MAX_RESULTS, 
    DEFAULT_SORT_BY, 
    DEFAULT_SORT_ORDER,
    ARXIV_CATEGORIES
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArxivPaper:
    """Represents a single arXiv paper."""
    
    def __init__(self, entry):
        self.id = entry.id.split('/')[-1]  # Extract arXiv ID
        self.title = entry.title.replace('\n', ' ').strip()
        self.authors = [author.name for author in entry.authors]
        self.summary = entry.summary.replace('\n', ' ').strip()
        self.published = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')
        self.updated = datetime.strptime(entry.updated, '%Y-%m-%dT%H:%M:%SZ')
        self.categories = [tag.term for tag in entry.tags]
        self.pdf_url = None
        self.abs_url = entry.id
        
        # Find PDF URL
        for link in entry.links:
            if link.type == 'application/pdf':
                self.pdf_url = link.href
                break
    
    def __str__(self):
        return f"{self.title} ({self.id}) - {', '.join(self.authors[:3])}"
    
    def to_dict(self):
        """Convert to dictionary for easy serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'authors': self.authors,
            'summary': self.summary,
            'published': self.published.isoformat(),
            'updated': self.updated.isoformat(),
            'categories': self.categories,
            'pdf_url': self.pdf_url,
            'abs_url': self.abs_url
        }

class ArxivAPI:
    """Interface to the arXiv API."""
    
    def __init__(self):
        self.base_url = ARXIV_BASE_URL
        self.delay = REQUEST_DELAY
    
    def search(self, 
               query: str, 
               max_results: int = DEFAULT_MAX_RESULTS,
               sort_by: str = DEFAULT_SORT_BY,
               sort_order: str = DEFAULT_SORT_ORDER,
               categories: Optional[List[str]] = None) -> List[ArxivPaper]:
        """
        Search arXiv for papers matching the query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            sort_by: Sort criteria (relevance, lastUpdatedDate, submittedDate)
            sort_order: Sort order (ascending, descending)
            categories: List of arXiv categories to search in
            
        Returns:
            List of ArxivPaper objects
        """
        
        # Build search query
        search_query = self._build_search_query(query, categories)
        
        # Build URL parameters
        params = {
            'search_query': search_query,
            'start': 0,
            'max_results': max_results,
            'sortBy': sort_by,
            'sortOrder': sort_order
        }
        
        url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
        
        logger.info(f"Searching arXiv with query: {search_query}")
        logger.info(f"URL: {url}")
        
        try:
            # Make request with delay to be respectful
            time.sleep(self.delay)
            
            with urllib.request.urlopen(url) as response:
                feed_data = response.read()
            
            # Parse the Atom feed
            feed = feedparser.parse(feed_data)
            
            if feed.bozo:
                logger.warning("Feed parsing had issues, but continuing...")
            
            papers = []
            for entry in feed.entries:
                try:
                    paper = ArxivPaper(entry)
                    papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing paper entry: {e}")
                    continue
            
            logger.info(f"Found {len(papers)} papers")
            return papers
            
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            raise
    
    def _build_search_query(self, query: str, categories: Optional[List[str]] = None) -> str:
        """
        Build the search query string for arXiv API.
        
        Args:
            query: User's search query
            categories: Optional list of categories to search in
            
        Returns:
            Formatted search query string
        """
        # Start with the main query in title and abstract
        search_parts = [f"(ti:{query} OR abs:{query})"]
        
        # Add category constraints if specified
        if categories:
            category_parts = [f"cat:{cat}" for cat in categories if cat in ARXIV_CATEGORIES]
            if category_parts:
                search_parts.append(f"({' OR '.join(category_parts)})")
        
        return " AND ".join(search_parts)
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[ArxivPaper]:
        """
        Get a specific paper by its arXiv ID.
        
        Args:
            arxiv_id: The arXiv ID (e.g., "2301.07041")
            
        Returns:
            ArxivPaper object or None if not found
        """
        papers = self.search(f"id:{arxiv_id}", max_results=1)
        return papers[0] if papers else None
    
    @staticmethod
    def get_available_categories() -> Dict[str, str]:
        """Get available arXiv categories."""
        return ARXIV_CATEGORIES.copy()
    
    def search_by_author(self, author_name: str, max_results: int = DEFAULT_MAX_RESULTS) -> List[ArxivPaper]:
        """
        Search for papers by a specific author.
        
        Args:
            author_name: Name of the author to search for
            max_results: Maximum number of results
            
        Returns:
            List of ArxivPaper objects
        """
        return self.search(f"au:{author_name}", max_results=max_results)
    
    def search_recent(self, 
                     query: str, 
                     days: int = 7, 
                     max_results: int = DEFAULT_MAX_RESULTS) -> List[ArxivPaper]:
        """
        Search for recent papers (within specified days).
        
        Args:
            query: Search query
            days: Number of days to look back
            max_results: Maximum number of results
            
        Returns:
            List of ArxivPaper objects
        """
        papers = self.search(query, max_results=max_results, sort_by="submittedDate")
        
        # Filter by date (this is a simple filter, arXiv API doesn't support date ranges directly)
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_papers = [p for p in papers if p.published >= cutoff_date]
        return recent_papers
