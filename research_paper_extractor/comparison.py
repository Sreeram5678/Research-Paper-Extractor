from typing import Dict, Any, List, Set, Tuple
from .summarizer import extract_keywords
from .arxiv_api import ArxivPaper

class PaperComparator:
    """Compares two research papers for similarities."""

    @staticmethod
    def compare(paper1: Any, paper2: Any) -> Dict[str, Any]:
        """Compares two papers based on their metadata and content."""
        
        # Keyword comparison
        kw1 = {k.lower() for k, _ in extract_keywords(paper1.summary)}
        kw2 = {k.lower() for k, _ in extract_keywords(paper2.summary)}
        
        common_keywords = kw1.intersection(kw2)
        jaccard_similarity = len(common_keywords) / len(kw1.union(kw2)) if kw1.union(kw2) else 0

        # Author comparison
        authors1 = set(paper1.authors)
        authors2 = set(paper2.authors)
        common_authors = authors1.intersection(authors2)

        # Basic title similarity (word overlap)
        title_words1 = {w.lower() for w in paper1.title.split() if len(w) > 3}
        title_words2 = {w.lower() for w in paper2.title.split() if len(w) > 3}
        common_title_words = title_words1.intersection(title_words2)

        return {
            "common_keywords": list(common_keywords),
            "common_authors": list(common_authors),
            "common_title_words": list(common_title_words),
            "similarity_score": round(jaccard_similarity, 3),
            "combined_score": round((jaccard_similarity * 0.7) + (len(common_authors) * 0.1) + (len(common_title_words) * 0.2 / max(len(title_words1), 1)), 3)
        }

    @staticmethod
    def format_comparison_report(paper1: Any, paper2: Any, diff: Dict[str, Any]) -> str:
        """Formats the comparison result for CLI display."""
        lines = [
            f"\nComparing Papers:",
            f"1. {paper1.title[:70]}...",
            f"2. {paper2.title[:70]}...",
            f"\n" + "─" * 45,
            f"{'Metric':<20} | {'Result'}",
            "─" * 45,
            f"{'Similarity Score':<20} | {diff['similarity_score']}",
            f"{'Common Keywords':<20} | {len(diff['common_keywords'])}",
            f"{'Common Authors':<20} | {len(diff['common_authors'])}",
            f"{'Common Title Words':<20} | {len(diff['common_title_words'])}",
            "─" * 45,
        ]
        
        if diff["common_keywords"]:
            lines.append(f"\nCommon Keywords: {', '.join(diff['common_keywords'])}")
        
        if diff["common_authors"]:
            lines.append(f"Common Authors: {', '.join(diff['common_authors'])}")
            
        return "\n".join(lines)
