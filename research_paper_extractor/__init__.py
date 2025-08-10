"""
Research Paper Extractor

A Python tool that automatically downloads research papers from arXiv based on topics you specify.
Search by keywords, authors, categories, or specific paper IDs and download PDFs with ease!
"""

__version__ = "1.0.0"
__author__ = "Sreeram"
__email__ = "sreeram.lagisetty@gmail.com"
__github__ = "https://github.com/Sreeram5678/Research-Paper-Extractor"

from .arxiv_api import ArxivAPI, ArxivPaper
from .downloader import PaperDownloader
from .config import get_download_dir, sanitize_filename, sanitize_topic_name

__all__ = [
    "ArxivAPI",
    "ArxivPaper", 
    "PaperDownloader",
    "get_download_dir",
    "sanitize_filename",
    "sanitize_topic_name"
]
