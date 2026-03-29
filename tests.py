"""
Unit tests for research_paper_extractor.

Tests cover:
- Citation exporter (BibTeX, RIS, APA, plain)
- Analytics module
- Summarizer (keyword extraction + sentence selection)
- Watchlist CRUD operations (mocked)
- Utils (dedup, filter, sort, text helpers)
- Config manager
- Batch downloader ID detection
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers — build fake ArxivPaper objects without hitting the real API
# ---------------------------------------------------------------------------

def _make_entry(arxiv_id: str, title: str, authors: list,
                summary: str, published: str = '2024-01-15T00:00:00Z',
                categories: list = None, pdf_url: str = None):
    """Build a minimal feedparser entry-like object."""
    entry = SimpleNamespace()
    entry.id = f'http://arxiv.org/abs/{arxiv_id}'
    entry.title = title
    entry.authors = [SimpleNamespace(name=a) for a in authors]
    entry.summary = summary
    entry.published = published
    entry.updated = published
    entry.tags = [SimpleNamespace(term=c) for c in (categories or ['cs.AI'])]
    entry.links = []
    if pdf_url:
        link = SimpleNamespace(type='application/pdf', href=pdf_url)
        entry.links.append(link)
    return entry


def _make_paper(arxiv_id='2401.00001', title='Test Paper on Neural Networks',
                authors=None, summary=None, categories=None):
    from research_paper_extractor.arxiv_api import ArxivPaper
    if authors is None:
        authors = ['Alice Smith', 'Bob Jones', 'Carol White']
    if summary is None:
        summary = (
            'We propose a novel approach to training deep neural networks. '
            'Our method achieves state-of-the-art performance on multiple benchmarks. '
            'The key idea is to use a self-supervised contrastive learning objective. '
            'Experiments demonstrate significant improvements over existing baselines. '
            'The model is efficient and requires minimal computational resources.'
        )
    entry = _make_entry(
        arxiv_id=arxiv_id, title=title, authors=authors,
        summary=summary, categories=categories or ['cs.AI', 'cs.LG'],
        pdf_url=f'https://arxiv.org/pdf/{arxiv_id}',
    )
    return ArxivPaper(entry)


# ===========================================================================
# Test: ArxivPaper
# ===========================================================================

class TestArxivPaper(unittest.TestCase):

    def setUp(self):
        self.paper = _make_paper()

    def test_id_extracted(self):
        self.assertEqual(self.paper.id, '2401.00001')

    def test_repr(self):
        r = repr(self.paper)
        self.assertIn('ArxivPaper', r)
        self.assertIn('2401.00001', r)

    def test_eq_same_id(self):
        p2 = _make_paper()
        self.assertEqual(self.paper, p2)

    def test_eq_different_id(self):
        p2 = _make_paper(arxiv_id='2401.99999')
        self.assertNotEqual(self.paper, p2)

    def test_hash_consistency(self):
        p2 = _make_paper()
        self.assertEqual(hash(self.paper), hash(p2))

    def test_to_dict_keys(self):
        d = self.paper.to_dict()
        for key in ('id', 'title', 'authors', 'summary', 'published',
                    'updated', 'categories', 'pdf_url', 'abs_url'):
            self.assertIn(key, d)

    def test_set_deduplication(self):
        p1 = _make_paper()
        p2 = _make_paper()
        p3 = _make_paper(arxiv_id='2401.99999')
        s = {p1, p2, p3}
        self.assertEqual(len(s), 2)


# ===========================================================================
# Test: Citation Exporter
# ===========================================================================

class TestCitationExporter(unittest.TestCase):

    def setUp(self):
        self.papers = [_make_paper(), _make_paper(arxiv_id='2401.00002',
                                                    title='Graph Neural Network Survey',
                                                    authors=['Dave Brown'])]

    def test_bibtex_contains_at_article(self):
        from research_paper_extractor.citation_exporter import export_bibtex
        out = export_bibtex(self.papers)
        self.assertIn('@article{', out)
        self.assertIn('eprint', out)

    def test_ris_contains_ty(self):
        from research_paper_extractor.citation_exporter import export_ris
        out = export_ris(self.papers)
        self.assertIn('TY  - JOUR', out)
        self.assertIn('ER  - ', out)

    def test_apa_contains_arxiv(self):
        from research_paper_extractor.citation_exporter import export_apa
        out = export_apa(self.papers)
        self.assertIn('arXiv preprint', out)

    def test_plain_numbered(self):
        from research_paper_extractor.citation_exporter import export_plain
        out = export_plain(self.papers)
        self.assertIn('[1]', out)
        self.assertIn('[2]', out)

    def test_invalid_format_raises(self):
        from research_paper_extractor.citation_exporter import export_citations
        with self.assertRaises(ValueError):
            export_citations(self.papers, fmt='docx')

    def test_export_citations_dispatch(self):
        from research_paper_extractor.citation_exporter import export_citations
        for fmt in ('bibtex', 'ris', 'apa', 'plain'):
            result = export_citations(self.papers, fmt=fmt)
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)


# ===========================================================================
# Test: Analytics
# ===========================================================================

class TestAnalytics(unittest.TestCase):

    def setUp(self):
        from research_paper_extractor.arxiv_api import ArxivPaper
        self.papers = [
            _make_paper(arxiv_id='2401.00001', authors=['Alice Smith', 'Bob Jones']),
            _make_paper(arxiv_id='2401.00002', authors=['Alice Smith', 'Carol White'],
                        categories=['cs.LG']),
            _make_paper(arxiv_id='2401.00003', authors=['Dave Brown'],
                        categories=['cs.CV']),
        ]

    def test_total(self):
        from research_paper_extractor.analytics import analyze_papers
        stats = analyze_papers(self.papers)
        self.assertEqual(stats['total'], 3)

    def test_most_prolific_author(self):
        from research_paper_extractor.analytics import analyze_papers
        stats = analyze_papers(self.papers)
        self.assertEqual(stats['most_prolific_author'], 'Alice Smith')

    def test_avg_authors(self):
        from research_paper_extractor.analytics import analyze_papers
        stats = analyze_papers(self.papers)
        # (2 + 2 + 1) / 3 = 1.67
        self.assertAlmostEqual(stats['avg_authors_per_paper'], 1.67, places=1)

    def test_empty_returns_zero(self):
        from research_paper_extractor.analytics import analyze_papers
        stats = analyze_papers([])
        self.assertEqual(stats.get('total', 0), 0)

    def test_format_report_string(self):
        from research_paper_extractor.analytics import analyze_papers, format_analytics_report
        stats = analyze_papers(self.papers)
        report = format_analytics_report(stats)
        self.assertIn('PAPER ANALYTICS REPORT', report)
        self.assertIn('Alice Smith', report)


# ===========================================================================
# Test: Summarizer
# ===========================================================================

class TestSummarizer(unittest.TestCase):

    def setUp(self):
        self.paper = _make_paper()

    def test_extract_keywords_returns_list(self):
        from research_paper_extractor.summarizer import extract_keywords
        kws = extract_keywords(self.paper.summary, top_n=5)
        self.assertIsInstance(kws, list)
        self.assertLessEqual(len(kws), 5)
        # Each item is a (word, score) tuple
        for word, score in kws:
            self.assertIsInstance(word, str)

    def test_summarize_returns_sentences(self):
        from research_paper_extractor.summarizer import summarize_abstract
        bullets = summarize_abstract(self.paper.summary, max_sentences=3)
        self.assertIsInstance(bullets, list)
        self.assertGreater(len(bullets), 0)

    def test_summarize_paper_contains_title(self):
        from research_paper_extractor.summarizer import summarize_paper
        out = summarize_paper(self.paper)
        self.assertIn('Test Paper', out)
        self.assertIn('Keywords:', out)

    def test_short_abstract_returns_all(self):
        from research_paper_extractor.summarizer import summarize_abstract
        short = 'This paper proposes a new method. It is very effective.'
        result = summarize_abstract(short, max_sentences=5)
        self.assertIsInstance(result, list)


# ===========================================================================
# Test: Utils
# ===========================================================================

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.papers = [
            _make_paper('2401.00001', 'Alpha Paper', ['Zara X']),
            _make_paper('2401.00002', 'Beta Paper', ['Amy Y'], categories=['cs.LG']),
            _make_paper('2401.00003', 'Gamma Paper', ['Alice Smith']),
        ]

    def test_deduplicate(self):
        from research_paper_extractor.utils import deduplicate_papers
        duped = self.papers + [_make_paper('2401.00001')]
        result = deduplicate_papers(duped)
        self.assertEqual(len(result), 3)

    def test_filter_by_year(self):
        from research_paper_extractor.utils import filter_by_year
        result = filter_by_year(self.papers, start_year=2024, end_year=2024)
        self.assertEqual(len(result), 3)
        result_empty = filter_by_year(self.papers, start_year=2030)
        self.assertEqual(len(result_empty), 0)

    def test_filter_by_author(self):
        from research_paper_extractor.utils import filter_by_author
        result = filter_by_author(self.papers, 'alice')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, '2401.00003')

    def test_filter_by_category(self):
        from research_paper_extractor.utils import filter_by_category
        # paper[1] has categories=['cs.LG'], others have ['cs.AI', 'cs.LG'] or ['cs.AI']
        papers_with_distinct_cats = [
            _make_paper('2401.00001', categories=['cs.AI']),
            _make_paper('2401.00002', categories=['cs.LG']),
            _make_paper('2401.00003', categories=['cs.CV']),
        ]
        result = filter_by_category(papers_with_distinct_cats, 'cs.LG')
        self.assertEqual(len(result), 1)

    def test_sort_by_title_ascending(self):
        from research_paper_extractor.utils import sort_papers
        result = sort_papers(self.papers, by='title', ascending=True)
        titles = [p.title for p in result]
        self.assertEqual(titles, sorted(titles, key=str.lower))

    def test_papers_to_json(self):
        from research_paper_extractor.utils import papers_to_json
        js = papers_to_json(self.papers)
        data = json.loads(js)
        self.assertEqual(len(data), 3)
        self.assertIn('title', data[0])

    def test_truncate_text(self):
        from research_paper_extractor.utils import truncate_text
        self.assertEqual(truncate_text('hello', 10), 'hello')
        result = truncate_text('a' * 50, max_chars=10)
        self.assertEqual(len(result), 10)
        self.assertTrue(result.endswith('...'))

    def test_format_file_size(self):
        from research_paper_extractor.utils import format_file_size
        self.assertIn('B', format_file_size(500))
        self.assertIn('KB', format_file_size(2048))
        self.assertIn('MB', format_file_size(1024 * 1024 * 2))


# ===========================================================================
# Test: Config manager
# ===========================================================================

class TestConfigManager(unittest.TestCase):

    def test_get_defaults(self):
        from research_paper_extractor import config_manager
        val = config_manager.get('general', 'max_results', fallback='10')
        self.assertEqual(val, '10')

    def test_show_config_returns_string(self):
        from research_paper_extractor import config_manager
        out = config_manager.show_config()
        self.assertIsInstance(out, str)

    def test_get_max_results_from_config_is_int(self):
        from research_paper_extractor import config_manager
        val = config_manager.get_max_results_from_config()
        self.assertIsInstance(val, int)


# ===========================================================================
# Test: Batch downloader helpers
# ===========================================================================

class TestBatchDownloader(unittest.TestCase):

    def test_is_arxiv_id_new_format(self):
        from research_paper_extractor.batch_downloader import _is_arxiv_id
        self.assertTrue(_is_arxiv_id('2301.07041'))
        self.assertTrue(_is_arxiv_id('2301.07041v2'))

    def test_is_arxiv_id_old_format(self):
        from research_paper_extractor.batch_downloader import _is_arxiv_id
        self.assertTrue(_is_arxiv_id('cs/0301027'))

    def test_is_arxiv_id_rejects_query(self):
        from research_paper_extractor.batch_downloader import _is_arxiv_id
        self.assertFalse(_is_arxiv_id('attention mechanism transformer'))
        self.assertFalse(_is_arxiv_id('deep learning'))

    def test_load_batch_txt(self):
        from research_paper_extractor.batch_downloader import load_batch_file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt',
                                         delete=False, encoding='utf-8') as f:
            f.write('# comment\n')
            f.write('2301.07041\n')
            f.write('attention mechanism\n')
            f.write('\n')
            fname = f.name
        try:
            ids, queries = load_batch_file(fname)
            self.assertIn('2301.07041', ids)
            self.assertIn('attention mechanism', queries)
        finally:
            os.unlink(fname)

    def test_create_sample_batch_file(self):
        from research_paper_extractor.batch_downloader import create_sample_batch_file
        with tempfile.TemporaryDirectory() as tmpdir:
            fname = os.path.join(tmpdir, 'sample_batch.txt')
            create_sample_batch_file(fname)
            content = Path(fname).read_text(encoding='utf-8')
            self.assertIn('Batch', content)


# ===========================================================================
# Test: BibTeX Parser
# ===========================================================================

class TestBibtexParser(unittest.TestCase):

    def test_parse_simple_bib(self):
        from research_paper_extractor.bibtex_parser import parse_bibtex_file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.bib', delete=False) as f:
            f.write("""
            @article{paper1,
                title = {Attention is All You Need},
                author = {Vaswani, Ashish and Shazeer, Noam},
                journal = {arXiv:1706.03762},
                year = {2017}
            }
            """)
            fname = f.name
        try:
            entries = parse_bibtex_file(fname)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]['arxiv_id'], '1706.03762')
        finally:
            os.unlink(fname)

    def test_bib_entry_to_paper_obj(self):
        from research_paper_extractor.bibtex_parser import bib_entry_to_paper_obj
        from research_paper_extractor.arxiv_api import ArxivPaper
        entry = {
            'arxiv_id': '2301.07041',
            'title': 'Test Title',
            'author': 'Author 1 and Author 2'
        }
        mock = bib_entry_to_paper_obj(entry)
        self.assertIsNotNone(mock)
        paper = ArxivPaper(mock)
        self.assertEqual(paper.id, '2301.07041')
        self.assertIn('Author 1', paper.authors)


# ===========================================================================
# Test: Markdown Exporter
# ===========================================================================

class TestMarkdownExporter(unittest.TestCase):

    def test_paper_to_markdown_contains_fields(self):
        from research_paper_extractor.markdown_exporter import paper_to_markdown
        paper = {
            'arxiv_id': '2301.07041',
            'title': 'Test Paper',
            'authors': json.dumps(['Author A', 'Author B']),
            'abstract': 'This is a test abstract.',
            'tags': json.dumps(['tag1', 'tag2']),
            'notes': 'Great paper'
        }
        md = paper_to_markdown(paper)
        self.assertIn('# Test Paper', md)
        self.assertIn('arxiv_id: 2301.07041', md)
        self.assertIn('tag1', md)
        self.assertIn('Great paper', md)

    def test_export_library_to_markdown(self):
        from research_paper_extractor.markdown_exporter import export_library_to_markdown
        papers = [{
            'arxiv_id': '2301.07041',
            'title': 'Test Paper',
            'authors': ['A'],
            'abstract': 'B'
        }]
        with tempfile.TemporaryDirectory() as tmpdir:
            count = export_library_to_markdown(papers, tmpdir)
            self.assertEqual(count, 1)
            self.assertTrue(os.path.exists(os.path.join(tmpdir, '2301.07041.md')))


# ===========================================================================
# Test: Paper Comparator (AI Mocked)
# ===========================================================================

class TestPaperComparator(unittest.TestCase):

    def test_compare_basic(self):
        from research_paper_extractor.comparison import PaperComparator
        p1 = _make_paper('2401.00001', title='Neural Nets for Attention', summary='Attention mechanism is a key component in transformer models.')
        p2 = _make_paper('2401.00002', title='Deep Learning Transformers', summary='Transformers use attention mechanisms to process sequences.')
        
        diff = PaperComparator.compare(p1, p2)
        self.assertIn('similarity_score', diff)
        self.assertGreater(diff['similarity_score'], 0)

    @unittest.skipIf(ImportError, "google-generativeai not installed")
    @patch('google.generativeai.GenerativeModel')
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"})
    def test_ai_compare(self, mock_model):
        from research_paper_extractor.comparison import PaperComparator
        
        # Mocking the AI response
        mock_instance = mock_model.return_value
        mock_instance.generate_content.return_value.text = "These papers are similar."
        
        p1 = _make_paper()
        p2 = _make_paper(arxiv_id='2401.00002')
        
        report = PaperComparator.ai_compare(p1, p2)
        mock_instance.generate_content.assert_called_once()


# ===========================================================================
# Test: Search History
# ===========================================================================

class TestSearchHistory(unittest.TestCase):

    def setUp(self):
        self.tmp_hist = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.tmp_hist.close()
        from research_paper_extractor.history import SearchHistory
        self.h = SearchHistory(history_file=self.tmp_hist.name)

    def tearDown(self):
        if os.path.exists(self.tmp_hist.name):
            os.unlink(self.tmp_hist.name)

    def test_add_and_get_history(self):
        self.h.add_entry("attention", results_count=5)
        self.h.add_entry("transformers", results_count=10)
        
        hist = self.h.get_history()
        self.assertEqual(len(hist), 2)
        self.assertEqual(hist[0]["query"], "transformers")
        self.assertEqual(hist[1]["query"], "attention")


# ===========================================================================
# Test: Semantic Scholar
# ===========================================================================

class TestSemanticScholar(unittest.TestCase):

    @patch('requests.get')
    def test_search_ss(self, mock_get):
        from research_paper_extractor.semantic_scholar import (
            SemanticScholarAPI, SSPaper
        )
        
        # Mocking the SS response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": [
                {
                    "paperId": "ss_id_123",
                    "title": "SS Paper",
                    "authors": [{"name": "Author X"}],
                    "abstract": "SS abstract",
                    "year": 2023,
                    "externalIds": {"ArXiv": "2301.12345"}
                }
            ]
        }
        
        api = SemanticScholarAPI()
        papers = api.search("test queries")
        
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].title, "SS Paper")
        self.assertEqual(papers[0].id, "2301.12345")
        self.assertEqual(papers[0].authors, ["Author X"])


# ===========================================================================
# Test: Library
# ===========================================================================

class TestPaperLibrary(unittest.TestCase):

    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.db_file.close()
        from research_paper_extractor.library import PaperLibrary
        self.lib = PaperLibrary(db_path=Path(self.db_file.name))
        self.paper = _make_paper()

    def tearDown(self):
        os.unlink(self.db_file.name)

    def test_add_and_retrieve(self):
        self.lib.add_paper(self.paper)
        record = self.lib.get_paper(self.paper.id)
        self.assertIsNotNone(record)
        self.assertEqual(record['arxiv_id'], self.paper.id)

    def test_duplicate_add_returns_false(self):
        self.lib.add_paper(self.paper)
        result = self.lib.add_paper(self.paper)
        self.assertFalse(result)

    def test_mark_read(self):
        self.lib.add_paper(self.paper)
        self.lib.mark_read(self.paper.id, read=True)
        record = self.lib.get_paper(self.paper.id)
        self.assertEqual(record['read'], 1)

    def test_set_rating(self):
        self.lib.add_paper(self.paper)
        self.lib.set_rating(self.paper.id, 4)
        record = self.lib.get_paper(self.paper.id)
        self.assertEqual(record['rating'], 4)

    def test_invalid_rating_raises(self):
        self.lib.add_paper(self.paper)
        with self.assertRaises(ValueError):
            self.lib.set_rating(self.paper.id, 6)

    def test_add_and_remove_tag(self):
        self.lib.add_paper(self.paper)
        self.lib.add_tag(self.paper.id, 'ml')
        record = self.lib.get_paper(self.paper.id)
        tags = json.loads(record['tags'])
        self.assertIn('ml', tags)
        self.lib.remove_tag(self.paper.id, 'ml')
        record = self.lib.get_paper(self.paper.id)
        tags = json.loads(record['tags'])
        self.assertNotIn('ml', tags)

    def test_get_all_tags(self):
        self.lib.add_paper(self.paper)
        self.lib.add_tag(self.paper.id, 'ml')
        p2 = _make_paper(arxiv_id='2401.00002')
        self.lib.add_paper(p2)
        self.lib.add_tag(p2.id, 'ai')
        all_tags = self.lib.get_all_tags()
        self.assertEqual(all_tags, ['ai', 'ml'])

    def test_add_tags_bulk(self):
        self.lib.add_paper(self.paper)
        p2 = _make_paper(arxiv_id='2401.00002')
        self.lib.add_paper(p2)
        count = self.lib.add_tags_bulk([self.paper.id, p2.id], 'reviewed')
        self.assertEqual(count, 2)
        self.assertIn('reviewed', json.loads(self.lib.get_paper(self.paper.id)['tags']))
        self.assertIn('reviewed', json.loads(self.lib.get_paper(p2.id)['tags']))

    def test_add_note(self):
        self.lib.add_paper(self.paper)
        self.lib.add_note(self.paper.id, 'Great read!')
        record = self.lib.get_paper(self.paper.id)
        self.assertEqual(record['notes'], 'Great read!')

    def test_update_paper_metadata(self):
        self.lib.add_paper(self.paper)
        updated = self.lib.update_paper_metadata(self.paper.id, {'citation_count': 42})
        self.assertTrue(updated)
        record = self.lib.get_paper(self.paper.id)
        self.assertEqual(record['citation_count'], 42)

    def test_remove_paper(self):
        self.lib.add_paper(self.paper)
        removed = self.lib.remove_paper(self.paper.id)
        self.assertTrue(removed)
        self.assertIsNone(self.lib.get_paper(self.paper.id))

    def test_stats(self):
        self.lib.add_paper(self.paper)
        stats = self.lib.get_stats()
        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['unread'], 1)


# ===========================================================================
# Entry point
# ===========================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
