# Research Paper Extractor

A powerful Python CLI toolkit for searching, downloading, and **managing** research papers from arXiv. Version 2.0 expands far beyond simple downloads — it includes a local library, citation export, research analytics, daily digests, watchlists, and much more.

## Features

### Core
- **Smart Search** — Search by keywords, topics, or phrases
- **Author Search** — Find all papers by a specific researcher
- **Category Filtering** — Filter by arXiv categories (cs.AI, cs.LG, cs.CV, etc.)
- **Recent Papers** — Show papers from the last N days
- **Batch Download** — Download multiple papers at once
- **Download by ID** — Fetch a specific paper by its arXiv ID
- **Preview Mode** — Browse results without downloading
- **Interactive Mode** — Guided interface for first-time users
- **Manifest Files** — Save a JSON manifest of every download session

### Research Tools (New in v2.0)
- **Local Library** — Tag, rate, annotate, and track your reading list (SQLite)
- **Citation Export** — Export to BibTeX, RIS, APA, or plain text
- **Analytics** — Publication trends, top authors, keyword frequency, collaboration stats
- **Abstract Summaries** — TF-IDF based key-point extraction (no AI API needed)
- **Watchlists** — Subscribe to keywords and authors; get alerts for new papers
- **Daily Digests** — Auto-generate markdown digests of the latest research
- **Citation Counts** — Look up citation counts via Semantic Scholar
- **Related Papers** — Discover papers similar to one you already have
- **Open in Browser** — Instantly open an arXiv abstract or PDF in your browser
- **Paper Info** — Inspect paper metadata without downloading
- **Config Management** — Persistent INI-based user settings
- **Batch Processing** — Process .txt or .csv lists of IDs and queries

## Installation

1. **Clone** this repository:
   ```bash
   git clone https://github.com/Sreeram5678/Research-Paper-Extractor
   cd Research-Paper-Extractor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

```bash
# Search and download papers
python main.py search "transformer architecture" --max-results 5

# Preview only (no download)
python main.py search "diffusion models" --preview-only

# Download a specific paper
python main.py download-by-id 1706.03762

# Look up paper info without downloading
python main.py info 1706.03762

# Open a paper in your browser
python main.py open 1706.03762
```

## Available Commands

### Search & Download

| Command | Description |
|---|---|
| `search QUERY` | Search arXiv and download papers |
| `download-by-id ID` | Download a specific paper by arXiv ID |
| `search-by-author NAME` | Find papers by a researcher |
| `interactive` | Guided interactive search session |
| `batch FILE` | Download from a .txt/.csv batch file |
| `categories` | List all available arXiv categories |

**Key `search` options:**
- `--max-results, -n` — Number of papers (default: from config)
- `--download-dir, -d` — Download directory
- `--categories, -c` — Filter by arXiv category (repeatable)
- `--sort-by` — Sort by `relevance`, `lastUpdatedDate`, or `submittedDate`
- `--recent-days` — Only papers from the last N days
- `--preview-only, -p` — See results without downloading
- `--auto-download, -a` — Download without confirmation
- `--add-to-library, -l` — Add results to your local library
- `--manifest, -m` — Save a JSON manifest file after downloading

### Paper Info & Discovery

| Command | Description |
|---|---|
| `info ID` | Show paper metadata (no download) |
| `summarize ID` | TF-IDF abstract key-point extraction |
| `related ID` | Find papers related to a given arXiv paper |
| `open ID` | Open abstract (or PDF) in default browser |
| `citations QUERY` | Look up citation counts via Semantic Scholar |

### Library Management (`library`)

| Sub-command | Description |
|---|---|
| `library add ID` | Add a paper by arXiv ID |
| `library list` | List library papers (filter by tag/rating/read) |
| `library mark-read ID` | Mark paper as read |
| `library rate ID 1-5` | Rate a paper 1–5 stars |
| `library note ID "text"` | Add a personal note |
| `library tag ID TAG` | Tag a paper |
| `library remove ID` | Remove a paper from library |
| `library stats` | Show library statistics |

### Watchlist & Alerts (`watch`)

| Sub-command | Description |
|---|---|
| `watch add-keyword TERM` | Subscribe to a keyword |
| `watch add-author NAME` | Subscribe to an author |
| `watch remove-keyword TERM` | Unsubscribe keyword |
| `watch remove-author NAME` | Unsubscribe author |
| `watch list` | Show your current watchlist |
| `watch clear` | Clear all watchlist entries |
| `check-alerts` | Fetch new papers for all subscriptions |

### Export & Analysis

| Command | Description |
|---|---|
| `export QUERY` | Export citations (BibTeX, RIS, APA, plain) |
| `analyze QUERY` | Run analytics on a set of search results |
| `digest` | Generate a markdown daily research digest |

### Configuration (`config`)

| Sub-command | Description |
|---|---|
| `config show` | Display current settings |
| `config set SECTION KEY VALUE` | Update a setting |
| `config reset` | Reset all settings to defaults |

## arXiv Categories

Common categories for use with `--categories`:

| Category | Description |
|---|---|
| `cs.AI` | Artificial Intelligence |
| `cs.LG` | Machine Learning |
| `cs.CV` | Computer Vision |
| `cs.CL` | Computation and Language (NLP) |
| `cs.NE` | Neural and Evolutionary Computing |
| `stat.ML` | Machine Learning (Statistics) |
| `cs.IR` | Information Retrieval |
| `cs.RO` | Robotics |

Run `python main.py categories` for the full list.

## File Organization

Downloads are organized automatically by topic:

```
downloads/
├── transformer_architecture/
│   ├── Attention_Is_All_You_Need_1706.03762.pdf
│   └── ...
├── author_geoffrey_hinton/
│   └── ...
├── batch_download/
│   └── ...
└── watchlist_alerts/
    └── ...
```

## Configuration

User settings are stored in `~/.arxiv_config.ini`. Manage via:

```bash
python main.py config show
python main.py config set general max_results 20
python main.py config set general download_dir ~/Papers
```

## Dependencies

- `requests` — HTTP requests
- `feedparser` — arXiv Atom feed parsing
- `beautifulsoup4` — HTML parsing
- `lxml` — XML/HTML processing
- `tqdm` — Progress bars
- `click` — CLI framework
- `python-dateutil` — Date handling

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and pull request guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a full history of releases.

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**For detailed examples and advanced usage, see [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)**

For help on any command: `python main.py COMMAND --help`

## Author

**Name**: Sreeram  
**Email**: sreeram.lagisetty@gmail.com  
**GitHub**: [Sreeram5678](https://github.com/Sreeram5678)  

**Repository**: [Research Paper Extractor](https://github.com/Sreeram5678/Research-Paper-Extractor)
