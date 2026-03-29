# Research Paper Extractor v2.1

A powerful Python CLI tool to search, download, analyse, and manage research papers from arXiv. Search by keywords, authors, categories, or specific paper IDs — then export citations, generate digests, manage a personal library, and much more.

## ✨ Features (v2.1)

### Core
| Feature | Command |
|---------|---------|
| Keyword search + download | `search` |
| Download by arXiv ID | `download-by-id` |
| Find papers by author | `search-by-author` |
| Interactive guided mode | `interactive` |
| List arXiv categories | `categories` |

### New in v2.x
| Feature | Command |
|---------|---------|
| 📋 Citation export (BibTeX / RIS / APA / plain) | `export` |
| 📊 Analytics on search results | `analyze` |
| 📝 TF-IDF abstract summariser | `summarize` |
| 🔔 Keyword/author watchlist management | `watch` |
| 📬 Check watchlist for new papers | `check-alerts` |
| 📚 Local SQLite paper library (read/tag/rate/notes) | `library` |
| 📁 Batch download from .txt / .csv file | `batch` |
| 📰 Daily markdown digest generator | `digest` |
| 📈 Citation count lookup (Semantic Scholar) | `citations` |
| 🔗 Related paper discovery | `related` |
| ⚙️ User config file management | `config` |

---

## Installation

```bash
git clone https://github.com/Sreeram5678/Research-Paper-Extractor.git
cd Research-Paper-Extractor
pip install -r requirements.txt
```

---

## Quick Start

```bash
# Search and download
python main.py search "transformer architecture" -n 5

# Preview only (no download)
python main.py search "diffusion models" --preview-only

# Download a specific paper
python main.py download-by-id 1706.03762

# Export citations from a search
python main.py export "attention mechanism" -f bibtex -o refs.bib

# Summarise paper abstracts
python main.py summarize 1706.03762

# Analyse search results
python main.py analyze "large language models" -n 50

# Generate a daily digest
python main.py digest -c cs.AI -c cs.LG -d 3

# Check for new papers in your watchlist
python main.py watch add-keyword "diffusion models"
python main.py check-alerts --days 7
```

---

## Command Reference

### Core Commands

```
search          Search arXiv and optionally download results
download-by-id  Download a specific paper by arXiv ID
search-by-author Search for papers by a researcher's name
categories      List all available arXiv categories
interactive     Guided interactive search interface
```

### Citation & Analysis

```
export          Export citations (bibtex | ris | apa | plain)
analyze         Run analytics on search result collections
summarize       Display TF-IDF key-point summaries of abstracts
citations       Look up citation counts via Semantic Scholar
related         Discover papers related to a given arXiv paper
```

### Personal Management

```
watch           Manage watchlist (add-keyword / add-author / list / clear)
check-alerts    Scan arXiv for new papers matching your watchlist
library         SQLite paper library (add / list / rate / tag / note / stats)
batch           Bulk download from a .txt or .csv batch file
digest          Generate a markdown daily digest of recent papers
config          View and edit user preferences
```

---

## Usage Examples

### Search with Filters
```bash
python main.py search "graph neural networks" \
  -c cs.LG -c cs.AI \
  --sort-by submittedDate \
  --recent-days 30 \
  -n 10
```

### Export BibTeX Citations
```bash
python main.py export "vision transformers" -f bibtex -o refs.bib
python main.py export "contrastive learning" -f apa
```

### Analytics on a Topic
```bash
python main.py analyze "federated learning" -n 100 -o report.txt
```

### Summarise Papers
```bash
python main.py summarize 2301.07041                         # by arXiv ID
python main.py summarize "RLHF" --is-query -n 5            # by search query
```

### Manage Your Library
```bash
python main.py library add 1706.03762
python main.py library rate 1706.03762 5
python main.py library note 1706.03762 "Foundational transformer paper"
python main.py library tag 1706.03762 must-read
python main.py library list --unread
python main.py library stats
```

### Watchlist & Alerts
```bash
python main.py watch add-keyword "diffusion models"
python main.py watch add-author "Yann LeCun"
python main.py watch list
python main.py check-alerts --days 3
```

### Batch Download
```bash
# Create a sample batch file first
python main.py batch --create-sample my_batch.txt
# Or use the included example
python main.py batch example_batch.txt --max-per-query 3 --preview-only
```

### Daily Digest
```bash
python main.py digest -c cs.AI -c cs.CL -d 1 -o digests/
python main.py digest -k "LLM fine-tuning" -k "RLHF" --print-only
```

### User Config
```bash
python main.py config show
python main.py config set general max_results 20
python main.py config set general download_dir ~/Papers
python main.py config reset
```

---

## arXiv Categories

40+ categories are supported. Some highlights:

| Category | Description |
|----------|-------------|
| `cs.AI`  | Artificial Intelligence |
| `cs.LG`  | Machine Learning |
| `cs.CV`  | Computer Vision |
| `cs.CL`  | Computation and Language (NLP) |
| `cs.RO`  | Robotics |
| `stat.ML` | Machine Learning (Statistics) |
| `quant-ph` | Quantum Physics |
| `q-bio.NC` | Neurons and Cognition |
| `econ.EM` | Econometrics |

Run `python main.py categories` for the full list.

---

## File Organisation

Downloads are automatically organised by topic:

```
downloads/
├── machine_learning/
│   ├── Neural_Networks_2301.07041.pdf
│   └── manifest.json           ← JSON download manifest
├── author_yann_lecun/
│   └── ...
└── batch_download/
    └── ...
```

---

## Running Tests

```bash
python -m pytest tests.py -v
# 47 tests, all passing on Python 3.13
```

---

## Dependencies

All standard-library friendly — no heavy ML dependencies required:

- `feedparser` — parse arXiv Atom feed
- `click` — CLI framework
- `tqdm` — download progress bars
- `requests`, `beautifulsoup4`, `lxml` — HTTP and HTML utilities

New features use only stdlib: `sqlite3`, `json`, `configparser`, `csv`, `re`, `math`, `urllib`.

---

## Tips & Best Practices

1. Start with `--preview-only` before downloading
2. Use `export -f bibtex` to build a BibTeX database as you go
3. Schedule `check-alerts` as a daily cron job for automatic updates
4. Use `analyze` with `-n 100` for meaningful keyword statistics
5. The library's `rate` and `tag` commands are great for paper reading workflows
6. `digest` + `--print-only` pipes well into other tools

---

## Contributing

Pull requests welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE).

---

**Author**: Sreeram Lagisetty  
**GitHub**: [Sreeram5678/Research-Paper-Extractor](https://github.com/Sreeram5678/Research-Paper-Extractor)
