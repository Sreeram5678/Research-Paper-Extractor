"""
Markdown exporter for research papers, compatible with Obsidian and Notion.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def paper_to_markdown(paper_dict: Dict[str, Any]) -> str:
    """
    Convert a paper dictionary to a rich Markdown string with YAML frontmatter.
    """
    # Parse JSON fields if they are strings
    authors = paper_dict.get('authors', [])
    if isinstance(authors, str):
        authors = json.loads(authors)
        
    categories = paper_dict.get('categories', [])
    if isinstance(categories, str):
        categories = json.loads(categories)
        
    tags = paper_dict.get('tags', [])
    if isinstance(tags, str):
        tags = json.loads(tags)

    # Frontmatter
    md = "---\n"
    md += f"title: \"{paper_dict.get('title', '').replace('\"', '\\\"')}\"\n"
    md += f"arxiv_id: {paper_dict.get('arxiv_id')}\n"
    md += f"authors: [{', '.join(authors)}]\n"
    md += f"published: {paper_dict.get('published', '')}\n"
    md += f"url: {paper_dict.get('abs_url', '')}\n"
    md += f"tags: [{', '.join(tags)}]\n"
    md += "---\n\n"

    # Content
    md += f"# {paper_dict.get('title')}\n\n"
    md += f"**Authors**: {', '.join(authors)}\n\n"
    md += f"**arXiv ID**: [{paper_dict.get('arxiv_id')}]({paper_dict.get('abs_url')})\n\n"
    
    md += "## Abstract\n\n"
    md += f"{paper_dict.get('abstract', 'No abstract available.')}\n\n"
    
    if paper_dict.get('notes'):
        md += "## Notes\n\n"
        md += f"{paper_dict['notes']}\n\n"
        
    md += "## Metadata\n\n"
    md += f"- **Categories**: {', '.join(categories)}\n"
    md += f"- **Added on**: {paper_dict.get('added_at', 'Unknown')}\n"
    md += f"- **Rating**: {'★' * (paper_dict.get('rating') or 0)}\n"
    
    return md

def export_library_to_markdown(papers: List[Dict[str, Any]], output_dir: str) -> int:
    """
    Export a list of papers to individual Markdown files in a directory.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for p in papers:
        # Sanitize filename
        filename = p.get('arxiv_id', 'unknown').replace('/', '_') + ".md"
        file_path = out_path / filename
        
        try:
            content = paper_to_markdown(p)
            file_path.write_text(content, encoding='utf-8')
            count += 1
        except Exception as e:
            logger.error(f"Failed to export MD for {p.get('arxiv_id')}: {e}")
            
    return count
