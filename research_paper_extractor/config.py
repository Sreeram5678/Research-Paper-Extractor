"""
Configuration settings for the arXiv paper downloader.
"""

import os
from pathlib import Path

# arXiv API settings
ARXIV_BASE_URL = "http://export.arxiv.org/api/query"
ARXIV_PDF_BASE_URL = "https://arxiv.org/pdf"

# Default download settings
DEFAULT_MAX_RESULTS = 10
DEFAULT_DOWNLOAD_DIR = "downloads"
DEFAULT_SORT_BY = "relevance"  # Options: relevance, lastUpdatedDate, submittedDate
DEFAULT_SORT_ORDER = "descending"  # Options: ascending, descending

# File settings
ALLOWED_EXTENSIONS = ['.pdf']
MAX_FILENAME_LENGTH = 100

# Rate limiting (to be respectful to arXiv servers)
REQUEST_DELAY = 1.0  # seconds between requests

# Search categories mapping (some popular ones)
ARXIV_CATEGORIES = {
    'cs.AI': 'Artificial Intelligence',
    'cs.LG': 'Machine Learning',
    'cs.CV': 'Computer Vision and Pattern Recognition',
    'cs.CL': 'Computation and Language',
    'cs.NE': 'Neural and Evolutionary Computing',
    'stat.ML': 'Machine Learning (Statistics)',
    'math.ST': 'Statistics Theory',
    'physics.data-an': 'Data Analysis, Statistics and Probability',
    'q-bio.QM': 'Quantitative Methods',
    'econ.EM': 'Econometrics',
    'cs.CR': 'Cryptography and Security',
    'cs.DB': 'Databases',
    'cs.IR': 'Information Retrieval',
    'cs.SE': 'Software Engineering',
    'cs.SY': 'Systems and Control',
    'math.OC': 'Optimization and Control',
    'stat.AP': 'Applications',
    'physics.comp-ph': 'Computational Physics'
}

def get_download_dir():
    """Get the download directory, creating it if it doesn't exist."""
    download_dir = Path(DEFAULT_DOWNLOAD_DIR)
    download_dir.mkdir(exist_ok=True)
    return download_dir

def sanitize_filename(filename):
    """Sanitize filename for safe saving."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > MAX_FILENAME_LENGTH:
        name, ext = os.path.splitext(filename)
        filename = name[:MAX_FILENAME_LENGTH - len(ext)] + ext
    
    return filename

def sanitize_topic_name(topic):
    """Sanitize topic name for use as folder name."""
    # Remove or replace invalid characters for folder names
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        topic = topic.replace(char, '_')
    
    # Replace spaces with underscores and convert to lowercase
    topic = topic.replace(' ', '_').lower()
    
    # Remove multiple underscores and leading/trailing underscores
    topic = '_'.join(filter(None, topic.split('_')))
    
    # Limit length for folder names
    max_folder_length = 50
    if len(topic) > max_folder_length:
        topic = topic[:max_folder_length].rstrip('_')
    
    return topic
