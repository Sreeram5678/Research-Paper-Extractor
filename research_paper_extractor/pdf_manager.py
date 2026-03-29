import os
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
from typing import Dict, Any, Optional

class PDFManager:
    """Manages PDF metadata extraction and text searching."""

    @staticmethod
    def get_metadata(file_path: str) -> Dict[str, Any]:
        """Extracts metadata from a PDF file using PyMuPDF."""
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            page_count = doc.page_count
            doc.close()

            return {
                "title": metadata.get("title", "N/A"),
                "author": metadata.get("author", "N/A"),
                "subject": metadata.get("subject", "N/A"),
                "keywords": metadata.get("keywords", "N/A"),
                "creator": metadata.get("creator", "N/A"),
                "producer": metadata.get("producer", "N/A"),
                "creation_date": metadata.get("creationDate", "N/A"),
                "mod_date": metadata.get("modDate", "N/A"),
                "page_count": page_count,
                "file_size": os.path.getsize(file_path)
            }
        except Exception as e:
            return {"error": f"Failed to extract metadata: {str(e)}"}

    @staticmethod
    def search_text(file_path: str, query: str, case_sensitive: bool = False) -> list:
        """Searches for a specific string inside a PDF file."""
        if not os.path.exists(file_path):
            return []

        results = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                search_text = text if case_sensitive else text.lower()
                search_query = query if case_sensitive else query.lower()

                if search_query in search_text:
                    # Find occurrences for context
                    lines = text.split('\n')
                    for line in lines:
                        if (search_query if case_sensitive else search_query.lower()) in (line if case_sensitive else line.lower()):
                            results.append({
                                "page": page_num + 1,
                                "context": line.strip()
                            })
            doc.close()
        except Exception:
            pass
        return results

    @staticmethod
    def extract_full_text(file_path: str) -> Optional[str]:
        """Extracts all text from a PDF file using pdfminer."""
        if not os.path.exists(file_path):
            return None
        try:
            return extract_text(file_path)
        except Exception:
            return None
