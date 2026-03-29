import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SSPaper:
    """Represents a paper from Semantic Scholar."""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("externalIds", {}).get("ArXiv", data.get("paperId"))
        self.ss_id = data.get("paperId")
        self.title = data.get("title", "N/A")
        self.authors = [a.get("name") for a in data.get("authors", []) if a.get("name")]
        self.summary = data.get("abstract", "No abstract available.")
        
        # Handle date
        year = data.get("year")
        pub_date = data.get("publicationDate")
        if pub_date:
            try:
                self.published = datetime.strptime(pub_date, "%Y-%m-%d")
            except ValueError:
                self.published = datetime(int(year), 1, 1) if year else datetime.now()
        else:
            self.published = datetime(int(year), 1, 1) if year else datetime.now()
            
        self.updated = self.published # SS doesn't usually provide separate update date
        self.categories = [f.get("category") for f in data.get("s2FieldsOfStudy", []) if f.get("category")]
        self.pdf_url = data.get("openAccessPdf", {}).get("url")
        self.abs_url = data.get("url")
        self.citation_count = data.get("citationCount", 0)
        self.venue = data.get("venue", "N/A")

    @property
    def id_v(self):
        """Compatibility property for ArxivPaper."""
        return self.id

    def to_bibtex(self) -> str:
        """Generate a BibTeX entry for this paper."""
        name = self.authors[0].split()[-1] if self.authors else "Unknown"
        year = self.published.year
        bib_id = f"{name}{year}"
        
        lines = [
            f"@article{{{bib_id},",
            f"  title = {{{self.title}}},",
            f"  author = {{{' and '.join(self.authors)}}},",
            f"  journal = {{Semantic Scholar ID: {self.ss_id}}},",
            f"  year = {{{year}}},",
            f"  url = {{{self.abs_url}}}"
        ]
        if self.id and 'v' not in self.id: # Likely arXiv ID
             lines.append(f"  eprint = {{{self.id}}},")
             lines.append(f"  archivePrefix = {{arXiv}}")
             
        lines.append("}")
        return "\n".join(lines)

    def to_dict(self):
        return {
            'id': self.id,
            'ss_id': self.ss_id,
            'title': self.title,
            'authors': self.authors,
            'summary': self.summary,
            'published': self.published.isoformat(),
            'updated': self.updated.isoformat(),
            'categories': self.categories,
            'pdf_url': self.pdf_url,
            'abs_url': self.abs_url,
            'citation_count': self.citation_count,
            'venue': self.venue
        }

class SemanticScholarAPI:
    """Interface to the Semantic Scholar API."""
    
    SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    FIELDS = "title,authors,abstract,year,publicationDate,s2FieldsOfStudy,openAccessPdf,url,citationCount,venue,externalIds"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.headers = {"x-api-key": api_key} if api_key else {}

    def search(self, query: str, max_results: int = 10) -> List[SSPaper]:
        """Search Semantic Scholar for papers."""
        params = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": self.FIELDS
        }
        
        try:
            logger.info(f"Searching Semantic Scholar for: {query}")
            response = requests.get(self.SEARCH_URL, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("data", [])
            
            papers = []
            for item in results:
                papers.append(SSPaper(item))
            
            return papers
        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []

    def get_paper_by_id(self, paper_id: str) -> Optional[SSPaper]:
        """Get paper details by ID (DOI, ArXiv ID, or SS ID)."""
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
        params = {"fields": self.FIELDS}
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            return SSPaper(response.json())
        except Exception as e:
            logger.error(f"Error fetching paper {paper_id} from Semantic Scholar: {e}")
            return None
