"""
Local paper library manager using SQLite.
Track downloaded papers, mark as read/unread, add tags and notes.
"""

import sqlite3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

from .arxiv_api import ArxivPaper

logger = logging.getLogger(__name__)

DEFAULT_LIBRARY_PATH = Path.home() / '.arxiv_library.db'


class PaperLibrary:
    """SQLite-backed local library for tracking arXiv papers."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the library.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.arxiv_library.db
        """
        self.db_path = db_path or DEFAULT_LIBRARY_PATH
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        """Get a database connection with row_factory set."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        with self._connect() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS papers (
                    arxiv_id       TEXT PRIMARY KEY,
                    title          TEXT NOT NULL,
                    authors        TEXT NOT NULL,  -- JSON list
                    abstract       TEXT,
                    categories     TEXT,           -- JSON list
                    published      TEXT,
                    abs_url        TEXT,
                    pdf_url        TEXT,
                    file_path      TEXT,
                    added_at       TEXT NOT NULL,
                    read           INTEGER NOT NULL DEFAULT 0,
                    rating         INTEGER,        -- 1-5 stars
                    notes          TEXT,
                    tags           TEXT,           -- JSON list
                    citation_count INTEGER,
                    last_synced    TEXT
                );

                CREATE TABLE IF NOT EXISTS tags (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    name    TEXT UNIQUE NOT NULL
                );
            ''')

    # ------------------------------------------------------------------ #
    # CRUD                                                                  #
    # ------------------------------------------------------------------ #

    def add_paper(self, paper: ArxivPaper, file_path: Optional[str] = None) -> bool:
        """
        Add a paper to the library.

        Args:
            paper: ArxivPaper to add
            file_path: Local file path if already downloaded

        Returns:
            True if inserted, False if already exists
        """
        try:
            with self._connect() as conn:
                conn.execute('''
                    INSERT OR IGNORE INTO papers
                        (arxiv_id, title, authors, abstract, categories,
                         published, abs_url, pdf_url, file_path, added_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                ''', (
                    paper.id,
                    paper.title,
                    json.dumps(paper.authors),
                    paper.summary,
                    json.dumps(paper.categories),
                    paper.published.isoformat(),
                    paper.abs_url,
                    paper.pdf_url,
                    file_path,
                    datetime.now(timezone.utc).isoformat(),
                ))
                return conn.execute('SELECT changes()').fetchone()[0] > 0
        except sqlite3.Error as e:
            logger.error(f'DB error adding paper {paper.id}: {e}')
            return False

    def remove_paper(self, arxiv_id: str) -> bool:
        """Remove a paper from the library by its arXiv ID."""
        with self._connect() as conn:
            conn.execute('DELETE FROM papers WHERE arxiv_id = ?', (arxiv_id,))
            return conn.execute('SELECT changes()').fetchone()[0] > 0

    def get_paper(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single paper's library record."""
        with self._connect() as conn:
            row = conn.execute('SELECT * FROM papers WHERE arxiv_id = ?', (arxiv_id,)).fetchone()
            return dict(row) if row else None

    def list_papers(self,
                    read: Optional[bool] = None,
                    tag: Optional[str] = None,
                    rating: Optional[int] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        """
        List papers in the library with optional filters.

        Args:
            read: Filter by read (True) / unread (False) status
            tag: Filter by tag name
            rating: Filter by minimum star rating
            limit: Maximum number of results

        Returns:
            List of paper record dicts
        """
        query = 'SELECT * FROM papers WHERE 1=1'
        params: List[Any] = []

        if read is not None:
            query += ' AND read = ?'
            params.append(1 if read else 0)

        if rating is not None:
            query += ' AND rating >= ?'
            params.append(rating)

        if tag is not None:
            # Tags stored as JSON list
            query += " AND tags LIKE ?"
            params.append(f'%"{tag}"%')

        query += ' ORDER BY added_at DESC LIMIT ?'
        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    # ------------------------------------------------------------------ #
    # Metadata updates                                                      #
    # ------------------------------------------------------------------ #

    def mark_read(self, arxiv_id: str, read: bool = True) -> bool:
        """Mark a paper as read or unread."""
        with self._connect() as conn:
            conn.execute('UPDATE papers SET read = ? WHERE arxiv_id = ?',
                         (1 if read else 0, arxiv_id))
            return conn.execute('SELECT changes()').fetchone()[0] > 0

    def set_rating(self, arxiv_id: str, rating: int) -> bool:
        """Set a star rating (1-5) for a paper."""
        if not 1 <= rating <= 5:
            raise ValueError('Rating must be between 1 and 5')
        with self._connect() as conn:
            conn.execute('UPDATE papers SET rating = ? WHERE arxiv_id = ?',
                         (rating, arxiv_id))
            return conn.execute('SELECT changes()').fetchone()[0] > 0

    def add_note(self, arxiv_id: str, note: str) -> bool:
        """Set a personal note for a paper."""
        with self._connect() as conn:
            conn.execute('UPDATE papers SET notes = ? WHERE arxiv_id = ?',
                         (note, arxiv_id))
            return conn.execute('SELECT changes()').fetchone()[0] > 0

    def add_tag(self, arxiv_id: str, tag: str) -> bool:
        """Add a tag to a paper."""
        record = self.get_paper(arxiv_id)
        if not record:
            return False
        tags = json.loads(record['tags'] or '[]')
        tag = tag.strip().lower()
        if tag not in tags:
            tags.append(tag)
        with self._connect() as conn:
            conn.execute('UPDATE papers SET tags = ? WHERE arxiv_id = ?',
                         (json.dumps(tags), arxiv_id))
            return True

    def remove_tag(self, arxiv_id: str, tag: str) -> bool:
        """Remove a tag from a paper."""
        record = self.get_paper(arxiv_id)
        if not record:
            return False
        tags = json.loads(record['tags'] or '[]')
        tag = tag.strip().lower()
        if tag in tags:
            tags.remove(tag)
        with self._connect() as conn:
            conn.execute('UPDATE papers SET tags = ? WHERE arxiv_id = ?',
                         (json.dumps(tags), arxiv_id))
            return True

    def get_all_tags(self) -> List[str]:
        """Return a list of all unique tags used in the library."""
        all_tags = set()
        with self._connect() as conn:
            rows = conn.execute('SELECT tags FROM papers WHERE tags IS NOT NULL').fetchall()
            for row in rows:
                tags = json.loads(row['tags'] or '[]')
                for t in tags:
                    all_tags.add(t)
        return sorted(list(all_tags))

    def add_tags_bulk(self, arxiv_ids: List[str], tag: str) -> int:
        """Add a tag to multiple papers."""
        count = 0
        for aid in arxiv_ids:
            if self.add_tag(aid, tag):
                count += 1
        return count

    def update_paper_metadata(self, arxiv_id: str, metadata: Dict[str, Any]) -> bool:
        """Update arbitrary metadata for a paper."""
        if not metadata:
            return False
            
        fields = []
        params = []
        for key, val in metadata.items():
            fields.append(f"{key} = ?")
            params.append(val if not isinstance(val, (list, dict)) else json.dumps(val))
            
        params.append(arxiv_id)
        query = f"UPDATE papers SET {', '.join(fields)} WHERE arxiv_id = ?"
        
        with self._connect() as conn:
            conn.execute(query, params)
            return conn.execute('SELECT changes()').fetchone()[0] > 0

    def set_file_path(self, arxiv_id: str, file_path: str) -> bool:
        """Update the local file path for a paper."""
        with self._connect() as conn:
            conn.execute('UPDATE papers SET file_path = ? WHERE arxiv_id = ?',
                         (file_path, arxiv_id))
            return conn.execute('SELECT changes()').fetchone()[0] > 0

    # ------------------------------------------------------------------ #
    # Statistics                                                            #
    # ------------------------------------------------------------------ #

    def get_stats(self) -> Dict[str, Any]:
        """Return library statistics."""
        with self._connect() as conn:
            total = conn.execute('SELECT COUNT(*) FROM papers').fetchone()[0]
            read_count = conn.execute('SELECT COUNT(*) FROM papers WHERE read=1').fetchone()[0]
            rated = conn.execute('SELECT COUNT(*) FROM papers WHERE rating IS NOT NULL').fetchone()[0]
            avg_rating = conn.execute('SELECT AVG(rating) FROM papers WHERE rating IS NOT NULL').fetchone()[0]
        return {
            'total': total,
            'read': read_count,
            'unread': total - read_count,
            'rated': rated,
            'avg_rating': round(avg_rating, 2) if avg_rating else None,
        }

    def format_library_list(self, papers: List[Dict[str, Any]]) -> str:
        """Format library paper list for CLI display."""
        if not papers:
            return 'Your library is empty.'
        lines = ['=' * 70, '  YOUR PAPER LIBRARY', '=' * 70]
        for i, p in enumerate(papers, 1):
            authors = json.loads(p.get('authors', '[]'))
            tags = json.loads(p.get('tags', '[]'))
            status = '✓' if p.get('read') else '○'
            rating = '★' * (p.get('rating') or 0) + '☆' * (5 - (p.get('rating') or 0))
            lines.append(f"\n{i:>3}. [{status}] {p['title'][:65]}")
            lines.append(f"     Authors : {', '.join(authors[:3])}{'...' if len(authors) > 3 else ''}")
            lines.append(f"     arXiv   : {p['arxiv_id']}  Added: {p['added_at'][:10]}")
            lines.append(f"     Rating  : {rating}   Tags: {', '.join(tags) if tags else 'none'}")
            if p.get('notes'):
                lines.append(f"     Notes   : {p['notes'][:80]}")
        lines.append(f'\n{"=" * 70}')
        return '\n'.join(lines)
    def export_to_csv(self, output_path: str) -> bool:
        """Export the entire library to a CSV file."""
        import csv
        papers = self.list_papers(limit=10000)
        if not papers:
            return False
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if not papers:
                    return False
                writer = csv.DictWriter(f, fieldnames=papers[0].keys())
                writer.writeheader()
                writer.writerows(papers)
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    def export_to_json(self, output_path: str) -> bool:
        """Export the entire library to a JSON file."""
        papers = self.list_papers(limit=10000)
        if not papers:
            return False
            
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(papers, f, indent=4)
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False

    def get_file_path(self, arxiv_id: str) -> Optional[str]:
        """Get the local file path for a paper."""
        record = self.get_paper(arxiv_id)
        return record.get('file_path') if record else None

    def export_to_bibtex(self, output_path: str) -> bool:
        """Export the entire library to a BibTeX file."""
        import json
        papers = self.list_papers(limit=10000)
        if not papers:
            return False
            
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for p in papers:
                    authors = " and ".join(json.loads(p['authors']))
                    clean_id = p['arxiv_id'].replace('/', '_')
                    entry = (
                        f"@article{{{clean_id},\n"
                        f"  title = {{{p['title']}}},\n"
                        f"  author = {{{authors}}},\n"
                        f"  journal = {{arXiv preprint arXiv:{p['arxiv_id']}}},\n"
                        f"  year = {{{p['published'][:4]}}},\n"
                        f"  url = {{{p['abs_url']}}}\n"
                        f"}}\n\n"
                    )
                    f.write(entry)
            return True
        except Exception as e:
            logger.error(f"Error exporting to BibTeX: {e}")
            return False
