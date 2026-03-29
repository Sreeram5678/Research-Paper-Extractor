# 🚀 Research Paper Extractor v2.0.0

A powerful, professional Python CLI toolkit for searching, downloading, and **managing** research papers from arXiv and Semantic Scholar. Version 2.0.0 is a complete modernization with 15+ new features for serious researchers.

## ✨ New in v2.0.0

- **Multi-Source Search** — Search both arXiv and Semantic Scholar simultaneously.
- **Interactive Shell** — Dedicated persistent shell mode for complex research workflows.
- **Paper Comparison** — Side-by-side analysis of similarity, authors, and keywords.
- **Recommendation Engine** — Suggests papers based on your library tags and search history.
- **RAKE Keyword Analysis** — Advanced Rapid Automatic Keyword Extraction for better summaries.
- **PDF Text Search (`grep-pdf`)** — Search for specific phrases *inside* your downloaded PDF collection.
- **CLI Themes** — Customizable color themes (Cyan, Green, Blue, Yellow, White).
- **Webhooks** — Instant Discord/Slack notifications for watchlist alerts.
- **Library Export** — Export your local library to **BibTeX**, CSV, or JSON.
- **HTML Digest** — Generate beautiful, styled HTML reports of daily research.
- **Visual Analytics** — ASCII bar charts for publication trends and category distributions.

## 🛠️ Installation

1. **Clone** this repository:
   ```bash
   git clone https://github.com/Sreeram5678/Research-Paper-Extractor
   cd Research-Paper-Extractor
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

```bash
# Enter the interactive shell (RECOMMENDED)
python main.py shell

# Search both arXiv and Semantic Scholar
python main.py search "latent diffusion" --source both

# Compare two papers
python main.py compare 1706.03762 2301.07041

# Search inside your downloaded PDFs
python main.py grep-pdf "positional encoding"

# Get personalized recommendations
python main.py recommend
```

## 📜 Available Commands

### Search & Discovery

| Command | Description |
|---|---|
| `search QUERY` | Search arXiv/Semantic Scholar and download papers |
| `shell` | **[NEW]** Enter interactive persistent shell mode |
| `recommend` | **[NEW]** Get paper suggestions based on activity |
| `compare ID1 ID2` | **[NEW]** Compare two papers side-by-side |
| `grep-pdf QUERY` | **[NEW]** Search text inside downloaded PDFs |
| `categories` | List all available arXiv categories |
| `info ID` | Show paper metadata (includes Semantic Scholar citations) |

### Library & Export

| Command | Description |
|---|---|
| `library list` | List library papers (filter by tag/rating/read) |
| `library export` | **[NEW]** Export library to **BibTeX**, CSV, or JSON |
| `digest` | Generate daily research digest (**MD** or **HTML**) |
| `analyze QUERY` | Run analytics with visual bar charts |
| `export QUERY` | Export search result citations to BibTeX/RIS |

### Watchlist & Config

| Command | Description |
|---|---|
| `check-alerts` | Fetch new papers and send **Webhook notifications** |
| `config theme` | **[NEW]** Switch between CLI color themes |
| `config show` | Display current settings (including URLs/Themes) |
| `watch list` | Manage your automated alerts |

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
