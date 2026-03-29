from typing import List, Dict, Any, Set
from .arxiv_api import ArxivAPI
from .library import PaperLibrary
from .history import SearchHistory
from .summarizer import extract_keywords
import collections

class Recommender:
    """Recommends papers based on library tags and search history."""

    def __init__(self):
        self.library = PaperLibrary()
        self.history = SearchHistory()
        self.api = ArxivAPI()

    def get_recommendations(self, limit: int = 5) -> List[Any]:
        """Suggests papers by finding trending keywords in your activity."""
        
        # 1. Collect keywords from library tags
        papers = self.library.list_papers(limit=100)
        all_tags = []
        for p in papers:
            import json
            tags = json.loads(p.get('tags', '[]'))
            all_tags.extend(tags)
            
        # 2. Collect keywords from history queries
        hist_entries = self.history.get_recent(limit=20)
        hist_queries = [e['query'] for e in hist_entries]
        
        # 3. Find most common terms
        common_terms = collections.Counter(all_tags + hist_queries).most_common(3)
        if not common_terms:
            return []

        # 4. Search for the top term
        top_term = common_terms[0][0]
        recommendations = self.api.search(top_term, max_results=limit)
        
        # 5. Filter out papers already in library
        existing_ids = {p['arxiv_id'] for p in papers}
        filtered = [r for r in recommendations if r.id not in existing_ids]
        
        return filtered[:limit]

    def format_recommendations(self, papers: List[Any]) -> str:
        """Formats recommendations for CLI display."""
        if not papers:
            return "No recommendations yet. Try searching for more papers or tagging your library!"
            
        lines = ["\n💡 RECOMMENDED FOR YOU", "─" * 30]
        for i, p in enumerate(papers, 1):
            lines.append(f"{i}. {p.title}")
            lines.append(f"   ID: {p.id} | {p.abs_url}")
        return "\n".join(lines)
