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

# Search categories mapping (comprehensive list of popular arXiv categories)
ARXIV_CATEGORIES = {
    # Computer Science
    'cs.AI':  'Artificial Intelligence',
    'cs.LG':  'Machine Learning',
    'cs.CV':  'Computer Vision and Pattern Recognition',
    'cs.CL':  'Computation and Language (NLP)',
    'cs.NE':  'Neural and Evolutionary Computing',
    'cs.RO':  'Robotics',
    'cs.CR':  'Cryptography and Security',
    'cs.DB':  'Databases',
    'cs.DC':  'Distributed, Parallel, and Cluster Computing',
    'cs.DS':  'Data Structures and Algorithms',
    'cs.GT':  'Computer Science and Game Theory',
    'cs.HC':  'Human-Computer Interaction',
    'cs.IR':  'Information Retrieval',
    'cs.IT':  'Information Theory',
    'cs.NA':  'Numerical Analysis',
    'cs.NI':  'Networking and Internet Architecture',
    'cs.PL':  'Programming Languages',
    'cs.SE':  'Software Engineering',
    'cs.SY':  'Systems and Control',
    # Statistics
    'stat.ML': 'Machine Learning (Statistics)',
    'stat.AP': 'Applications (Statistics)',
    'stat.ME': 'Methodology (Statistics)',
    'stat.TH': 'Statistics Theory',
    # Mathematics
    'math.ST': 'Statistics Theory (Math)',
    'math.OC': 'Optimization and Control',
    'math.PR': 'Probability',
    'math.CO': 'Combinatorics',
    'math.NA': 'Numerical Analysis',
    # Physics
    'physics.data-an':  'Data Analysis, Statistics and Probability',
    'physics.comp-ph':  'Computational Physics',
    'quant-ph':         'Quantum Physics',
    'astro-ph.IM':      'Astrophysics — Instrumentation and Methods',
    'cond-mat.dis-nn':  'Disordered Systems and Neural Networks',
    # Biology / Medicine
    'q-bio.QM':  'Quantitative Methods (Biology)',
    'q-bio.NC':  'Neurons and Cognition',
    'q-bio.GN':  'Genomics',
    'eess.SP':   'Signal Processing',
    'eess.AS':   'Audio and Speech Processing',
    # Economics
    'econ.EM':   'Econometrics',
    'econ.GN':   'General Economics',
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
