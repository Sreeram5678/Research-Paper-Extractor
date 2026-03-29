"""
Batch download from file module.
Reads a .txt or .csv file of search queries or arXiv IDs and downloads them all.
"""

import csv
import logging
from pathlib import Path
from typing import List, Tuple

from .arxiv_api import ArxivAPI, ArxivPaper

logger = logging.getLogger(__name__)


def _is_arxiv_id(token: str) -> bool:
    """
    Heuristically detect if a string looks like an arXiv ID.
    Supports formats like '2301.07041', 'cs/0301027', 'hep-th/9901001v2'.
    """
    import re
    # New format: YYMM.NNNNN or YYMM.NNNNNvN
    if re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', token):
        return True
    # Old format: cat/YYMMNNN
    if re.match(r'^[a-z\-]+/\d{7}(v\d+)?$', token):
        return True
    return False


def load_batch_file(filepath: str) -> Tuple[List[str], List[str]]:
    """
    Load a batch file and split entries into arXiv IDs and search queries.

    Supported file formats:
    - .txt: one entry per line
    - .csv: 'type,value' format where type is 'id' or 'query'

    Args:
        filepath: Path to the batch file

    Returns:
        Tuple of (arxiv_ids, queries)
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f'Batch file not found: {filepath}')

    arxiv_ids: List[str] = []
    queries: List[str] = []

    if path.suffix.lower() == '.csv':
        with open(path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                if len(row) >= 2:
                    entry_type = row[0].strip().lower()
                    value = row[1].strip()
                    if entry_type == 'id':
                        arxiv_ids.append(value)
                    elif entry_type == 'query':
                        queries.append(value)
                    else:
                        # Unknown type: auto-detect
                        if _is_arxiv_id(value):
                            arxiv_ids.append(value)
                        else:
                            queries.append(value)
                elif len(row) == 1:
                    value = row[0].strip()
                    if value:
                        if _is_arxiv_id(value):
                            arxiv_ids.append(value)
                        else:
                            queries.append(value)
    else:
        # Plain text: one entry per line
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if _is_arxiv_id(line):
                    arxiv_ids.append(line)
                else:
                    queries.append(line)

    logger.info(f'Loaded batch file: {len(arxiv_ids)} IDs, {len(queries)} queries')
    return arxiv_ids, queries


def resolve_batch(filepath: str,
                  max_results_per_query: int = 5) -> List[ArxivPaper]:
    """
    Resolve a batch file to a list of ArxivPaper objects.

    Args:
        filepath: Path to .txt or .csv batch file
        max_results_per_query: Max papers per search query

    Returns:
        Deduplicated list of ArxivPaper objects
    """
    arxiv_ids, queries = load_batch_file(filepath)
    api = ArxivAPI()
    papers: List[ArxivPaper] = []
    seen_ids = set()

    # Resolve by ID
    for arxiv_id in arxiv_ids:
        paper = api.get_paper_by_id(arxiv_id)
        if paper and paper.id not in seen_ids:
            papers.append(paper)
            seen_ids.add(paper.id)
        elif not paper:
            logger.warning(f'Could not find paper with ID: {arxiv_id}')

    # Resolve by query
    for query in queries:
        results = api.search(query, max_results=max_results_per_query)
        for paper in results:
            if paper.id not in seen_ids:
                papers.append(paper)
                seen_ids.add(paper.id)

    logger.info(f'Batch resolved: {len(papers)} unique papers')
    return papers


def create_sample_batch_file(output_path: str) -> None:
    """
    Create a sample batch file showing both supported formats.

    Args:
        output_path: Path for the sample file
    """
    sample = '''# ArXiv Batch Download File
# Lines starting with # are comments.
# Each line can be:
#   - An arXiv ID (e.g. 2301.07041)
#   - A search query (any text that is not an arXiv ID)

# arXiv IDs
2301.07041

# Search queries
attention mechanism transformer
graph neural networks survey
'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sample)
    logger.info(f'Sample batch file created: {output_path}')
