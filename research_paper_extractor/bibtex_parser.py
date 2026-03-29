"""
Simple BibTeX parser for ArXiv paper entries.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from .arxiv_api import ArxivPaper
from types import SimpleNamespace

logger = logging.getLogger(__name__)

def parse_bibtex_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse a .bib file and return a list of paper-like dicts.
    Specifically looks for arXiv IDs in the 'eprint' or 'journal' fields.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read BibTeX file {file_path}: {e}")
        return []

    # Simple regex to find entries: @article{key, ... }
    # This is a very basic parser and might fail on complex BibTeX
    entries = []
    
    # Split by @ symbols at the start of lines
    blocks = re.split(r'\n\s*@', '\n' + content)
    
    for block in blocks:
        if not block.strip():
            continue
            
        entry_type_match = re.match(r'^(\w+)\s*\{', block.strip())
        if not entry_type_match:
            continue
            
        entry_type = entry_type_match.group(1).lower()
        
        # Extract fields using regex
        # This is non-trivial for nested braces, but for arXiv it's usually simple
        fields = {}
        
        # Find all field = {value} or field = "value"
        field_matches = re.findall(r'(\w+)\s*=\s*[\{\"](.*?)[\}\"]', block, re.DOTALL)
        for key, val in field_matches:
            fields[key.lower().strip()] = val.strip()
            
        if fields:
            # Try to find an arXiv ID
            arxiv_id = fields.get('eprint') or fields.get('arxivId')
            if not arxiv_id and 'journal' in fields:
                # Often journal = {arXiv:2301.07041}
                match = re.search(r'arXiv:(\d{4}\.\d{4,5})', fields['journal'])
                if match:
                    arxiv_id = match.group(1)
            
            if arxiv_id:
                fields['arxiv_id'] = arxiv_id
                entries.append(fields)
                
    return entries

def bib_entry_to_paper_obj(entry: Dict[str, Any]) -> Optional[Any]:
    """
    Convert a BibTeX entry dict to a mock entry object that ArxivPaper can wrap.
    Note: This is useful if we only have the ID and want to fetch full metadata later.
    """
    arxiv_id = entry.get('arxiv_id')
    if not arxiv_id:
        return None
        
    # Create a mock feedparser-like entry
    mock = SimpleNamespace()
    mock.id = f"http://arxiv.org/abs/{arxiv_id}"
    mock.title = entry.get('title', 'Unknown Title')
    
    authors_str = entry.get('author', 'Unknown Author')
    # BibTeX authors are usually "Name1 and Name2 and Name3"
    authors_list = [a.strip() for a in authors_str.split(' and ')]
    mock.authors = [SimpleNamespace(name=a) for a in authors_list]
    
    mock.summary = entry.get('abstract', '')
    mock.published = entry.get('year', '2000') + "-01-01T00:00:00Z"
    mock.updated = mock.published
    mock.tags = [SimpleNamespace(term='imported')]
    mock.links = []
    
    return mock
