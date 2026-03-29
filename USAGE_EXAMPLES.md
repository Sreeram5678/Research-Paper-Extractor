# Research Paper Extractor v2.0 — Usage Examples

A comprehensive guide to every command available in the Research Paper Extractor CLI.

## Table of Contents

1. [Search & Download](#1-search--download)
2. [Download by ID](#2-download-by-id)
3. [Search by Author](#3-search-by-author)
4. [Interactive Mode](#4-interactive-mode)
5. [Paper Info](#5-paper-info)
6. [Open in Browser](#6-open-in-browser)
7. [Abstract Summarizer](#7-abstract-summarizer)
19. [BibTeX Management](#19-bibtex-management)
20. [Advanced Library Features](#20-advanced-library-features)
21. [AI Paper Comparison](#21-ai-paper-comparison)
22. [Full-Text PDF Search](#22-full-text-pdf-search)
23. [Webhook Notifications](#23-webhook-notifications)
24. [Search History & Analytics](#24-search-history--analytics)
25. [Research Workflow Examples](#25-research-workflow-examples)

---

## 1. Search & Download

### Basic search
```bash
# Download papers on a topic (creates downloads/machine_learning/)
python main.py search "machine learning"

# Limit number of results
python main.py search "deep learning" --max-results 5
python main.py search "quantum computing" -n 3
```

### Preview before downloading
```bash
# See results without downloading anything
python main.py search "neural networks" --preview-only
python main.py search "computer vision" -p
```

### Auto-download without confirmation
```bash
python main.py search "reinforcement learning" --auto-download
python main.py search "robotics" -a
```

### Filter by arXiv category
```bash
# Single category
python main.py search "machine learning" --categories cs.LG

# Multiple categories
python main.py search "AI research" -c cs.AI -c cs.LG -c cs.CV

# List all available categories
python main.py categories
```

### Sort results
```bash
python main.py search "transformers" --sort-by relevance       # default
python main.py search "GPT models" --sort-by lastUpdatedDate
python main.py search "BERT" --sort-by submittedDate
```

### Recent papers only
```bash
python main.py search "large language models" --recent-days 7
python main.py search "diffusion models" --recent-days 30 -n 10
```

### Add to library automatically
```bash
# Download and store in local library at the same time
python main.py search "federated learning" --auto-download --add-to-library
python main.py search "graph neural networks" -a -l
```

### Save a download manifest
```bash
# Creates a JSON file listing every paper downloaded in the session
python main.py search "attention mechanism" -a --manifest
python main.py search "computer vision" -a -m
```

### Custom download directory
```bash
python main.py search "federated learning" --download-dir ~/Research/Papers
python main.py search "edge computing" -d /path/to/papers
```

### Combining options
```bash
python main.py search "graph neural networks" \
  --max-results 10 \
  --categories cs.LG \
  --sort-by lastUpdatedDate \
  --recent-days 30 \
  --auto-download \
  --add-to-library \
  --manifest
```

---

## 2. Download by ID

```bash
# Download a specific paper by arXiv ID
python main.py download-by-id 1706.03762    # Attention Is All You Need
python main.py download-by-id 1412.6980    # Adam optimizer

# Custom filename
python main.py download-by-id 1706.03762 --filename "attention_is_all_you_need"
python main.py download-by-id 2301.07041 -f "my_paper"

# Custom directory
python main.py download-by-id 1706.03762 -d ~/Important_Papers
```

---

## 3. Search by Author

```bash
# Find papers by a researcher
python main.py search-by-author "Geoffrey Hinton"
python main.py search-by-author "Yann LeCun"
python main.py search-by-author "Andrew Ng"

# Limit results (useful for prolific authors)
python main.py search-by-author "Yoshua Bengio" --max-results 5

# Preview only
python main.py search-by-author "Fei-Fei Li" --preview-only

# Save to a specific folder
python main.py search-by-author "Demis Hassabis" -d ~/Research/DeepMind
```

---

## 4. Interactive Mode

```bash
# Start interactive session with an initial query
python main.py interactive --query "transformers"
python main.py interactive -q "machine learning"

# Set max results and directory upfront
python main.py interactive -q "deep learning" -n 15 -d ~/Research

# In the interactive session:
#   'all'   → download all papers found
#   '1,3,5' → download papers 1, 3, and 5
#   'new'   → start a new search
#   'none'  → skip downloads and continue
```

---

## 5. Paper Info

Display full paper metadata without downloading anything:

```bash
# Show title, authors, categories, abstract preview, and URLs
python main.py info 1706.03762

# Show the full abstract
python main.py info 2301.07041 --full-abstract
python main.py info 2301.07041 -a

# Show a TF-IDF summary of the abstract
python main.py info 2301.07041 --summarize
python main.py info 2301.07041 -s
```

---

## 6. Open in Browser

```bash
# Open the abstract page in your default browser
python main.py open 1706.03762

# Open the PDF directly
python main.py open 1706.03762 --pdf
```

---

## 7. Abstract Summarizer

Extract key points from paper abstracts using TF-IDF — no AI API needed:

```bash
# Summarize a single paper by arXiv ID
python main.py summarize 1706.03762

# Control the number of key points and keywords
python main.py summarize 2301.07041 --sentences 5 --keywords 10
python main.py summarize 2301.07041 -s 5 -k 10

# Summarize papers from a search query
python main.py summarize "attention mechanism" --is-query
python main.py summarize "graph neural networks" --is-query -n 3 -q
```

---

## 8. Citation Export

Export paper metadata in your preferred citation format:

```bash
# Default: BibTeX printed to stdout
python main.py export "transformer architecture"

# Save to a .bib file
python main.py export "transformers NLP" -f bibtex -o my_refs.bib

# RIS format (Zotero, EndNote, Mendeley)
python main.py export "graph neural networks" -f ris -o papers.ris

# APA 7th edition
python main.py export "deep learning survey" -f apa

# Plain text numbered references
python main.py export "attention mechanism" -f plain -o refs.txt

# Combine with category filters
python main.py export "machine learning" -c cs.LG -n 20 -f bibtex -o ml_refs.bib
```

**Supported formats:** `bibtex`, `ris`, `apa`, `plain`

---

## 9. Research Analytics

Analyze a set of search results for statistical insights:

```bash
# Analyze papers on a topic (50 papers by default)
python main.py analyze "machine learning"

# Analyze more papers for richer stats
python main.py analyze "deep learning" --max-results 100

# Filter by category before analyzing
python main.py analyze "computer vision" -c cs.CV -n 80

# Save the report to a file
python main.py analyze "NLP 2024" --output analytics_report.txt
```

The report includes:
- Publication trends by year (ASCII bar chart)
- Top 10 authors
- Top categories
- Collaboration size distribution (solo / small / medium / large teams)
- Top title keywords
- Top abstract keywords

---

## 10. Watchlists & Alerts

Subscribe to keywords and authors, then check for new papers on demand.

### Managing your watchlist
```bash
# Add a keyword
python main.py watch add-keyword "diffusion models"
python main.py watch add-keyword "federated learning"

# Add an author
python main.py watch add-author "Geoffrey Hinton"
python main.py watch add-author "Yann LeCun"

# View your watchlist
python main.py watch list

# Remove entries
python main.py watch remove-keyword "diffusion models"
python main.py watch remove-author "Geoffrey Hinton"

# Clear everything
python main.py watch clear
```

### Checking for new papers
```bash
# Check for papers from the last 7 days (default)
python main.py check-alerts

# Check a custom time window
python main.py check-alerts --days 3
python main.py check-alerts --days 14

# Fetch up to 20 papers per query
python main.py check-alerts -n 20

# Automatically download all found papers
python main.py check-alerts --download --download-dir ~/Alerts
```

---

## 11. Local Library

A persistent SQLite library to track your paper reading list:

### Adding papers
```bash
python main.py library add 1706.03762
python main.py library add 2301.07041

# Or add automatically when searching
python main.py search "transformers" -a -l
```

### Listing & filtering
```bash
# List all papers
python main.py library list

# Show only unread papers
python main.py library list --unread

# Show only read papers
python main.py library list --read

# Filter by tag
python main.py library list --tag "must-read"

# Filter by minimum rating
python main.py library list --rating 4

# Limit results
python main.py library list -n 20
```

### Organizing papers
```bash
# Mark as read
python main.py library mark-read 1706.03762

# Mark as unread
python main.py library mark-read 1706.03762 --unread

# Rate a paper (1–5 stars)
python main.py library rate 1706.03762 5
python main.py library rate 2301.07041 3

# Add a personal note
python main.py library note 1706.03762 "Foundational paper — must cite in chapter 2"

# Tag a paper
python main.py library tag 1706.03762 "must-read"
python main.py library tag 2301.07041 "NLP"

# Remove a tag
python main.py library tag 1706.03762 "must-read" --remove
```

### Removing & statistics
```bash
# Remove a paper from library
python main.py library remove 2301.07041

# Show library statistics
python main.py library stats
```

---

## 12. Batch Downloads

Process a list of arXiv IDs and/or search queries from a file:

### Creating and using batch files
```bash
# Generate a sample batch file to see the format
python main.py batch --create-sample my_papers.txt

# Download all papers in the batch file
python main.py batch my_papers.txt

# Preview without downloading
python main.py batch my_papers.txt --preview-only

# Set max results per query
python main.py batch my_papers.txt --max-per-query 10

# Download to a specific directory
python main.py batch my_papers.txt -d ~/BatchPapers

# Add to library automatically
python main.py batch my_papers.txt --add-to-library
```

### Batch file format (`.txt`)
```
# Lines starting with # are comments

# arXiv IDs are downloaded directly
1706.03762
2301.07041
1412.6980

# Anything else is treated as a search query
attention mechanism transformers
graph neural networks
diffusion models survey
```

### Batch file format (`.csv`)
```csv
id,1706.03762
id,2301.07041
query,attention mechanism
query,reinforcement learning survey
```

---

## 13. Daily Digest

Auto-generate a markdown digest of the latest papers:

```bash
# Default: cs.AI, cs.LG, cs.CL from the last 1 day
python main.py digest

# Specify categories
python main.py digest -c cs.AI -c cs.CV -c cs.RO

# Specify keywords instead
python main.py digest -k "diffusion models" -k "LLM alignment"

# Mix categories and keywords
python main.py digest -c cs.LG -k "foundation models"

# Extend the lookback window
python main.py digest -d 3       # last 3 days
python main.py digest -d 7       # last week

# More papers per category/keyword
python main.py digest -n 10

# Print to terminal instead of saving
python main.py digest --print-only
python main.py digest -p

# Save to a specific directory
python main.py digest --output-dir ~/Digests
```

---

## 14. Citation Counts

Look up citation counts from Semantic Scholar:

```bash
# Look up a single paper
python main.py citations 1706.03762 --is-id
python main.py citations 2301.07041 -i

# Look up citations for papers matching a query
python main.py citations "attention is all you need" -n 5
python main.py citations "BERT language model" -n 10
```

---

## 15. Related Papers

Find papers related to one you already have using TF-IDF keyword extraction:

```bash
# Find related papers for a given arXiv ID
python main.py related 1706.03762

# Get more results
python main.py related 1706.03762 --max-results 20
python main.py related 1706.03762 -n 20

# Find and download related papers
python main.py related 2301.07041 --download
python main.py related 2301.07041 -d --download-dir ~/Related
```

---

## 16. Configuration

Persistent settings stored in `~/.arxiv_config.ini`:

```bash
# View all current settings
python main.py config show

# Set default max results
python main.py config set general max_results 20

# Set default download directory
python main.py config set general download_dir ~/Papers

# Toggle abstract preview
python main.py config set display show_abstract_preview true

# Reset everything to defaults
python main.py config reset
```

---

## 17. Utility Commands

```bash
# List all available arXiv categories
python main.py categories

# Check version
python main.py --version

# Get help on any command
python main.py --help
python main.py search --help
python main.py library --help
python main.py watch --help
python main.py config --help
```

---

## 18. Research Workflow Examples

### Literature Review Workflow
```bash
# 1. Preview what's available
python main.py search "federated learning" -p -n 20

# 2. Download the most relevant papers with a manifest
python main.py search "federated learning" -c cs.LG -n 10 -a -l -m

# 3. Get seminal papers by ID
python main.py download-by-id 1602.05629   # Original FL paper

# 4. Export all for reference manager
python main.py export "federated learning" -c cs.LG -f bibtex -o fl_refs.bib

# 5. Run analytics to understand the field
python main.py analyze "federated learning" -c cs.LG -n 100
```

### Stay Current Workflow
```bash
# Subscribe to topics and authors
python main.py watch add-keyword "diffusion models"
python main.py watch add-keyword "LLM alignment"
python main.py watch add-author "Ilya Sutskever"

# Run daily (or add to a cron job)
python main.py check-alerts --days 1 --download

# Or generate a weekly digest instead
python main.py digest -k "diffusion models" -k "LLM" -d 7 -o ~/Weekly
```

### Paper Deep-Dive Workflow
```bash
# 1. Inspect a paper before downloading
python main.py info 1706.03762 --summarize

# 2. Open in browser for a quick scan
python main.py open 1706.03762

# 3. Download it and add to library
python main.py download-by-id 1706.03762
python main.py library add 1706.03762

# 4. Rate and annotate
python main.py library rate 1706.03762 5
python main.py library note 1706.03762 "Core architecture paper — cite in intro"
python main.py library tag 1706.03762 "must-read"

# 5. Discover follow-on work
python main.py related 1706.03762 -n 15

# 6. Check how many citations it has
python main.py citations 1706.03762 --is-id
```

### Batch Collection Workflow
```bash
# Create a batch file with your reading list
python main.py batch --create-sample reading_list.txt

# Edit reading_list.txt, then download everything at once
python main.py batch reading_list.txt --add-to-library -d ~/ReadingList

# Export the whole batch as citations
python main.py export "survey deep learning" -f bibtex -o all_refs.bib
```

---

## Quick Reference

| Command | Short Form | Description |
|---------|-----------|-------------|
| `search "topic"` | — | Search & download |
| `download-by-id ID` | — | Fetch by arXiv ID |
| `search-by-author "Name"` | — | Papers by author |
| `interactive -q "topic"` | — | Guided session |
| `info ID` | — | Metadata only |
| `open ID` | — | Open in browser |
| `summarize ID` | — | Key-point summary |
| `export "query" -f bibtex` | — | Export citations |
| `analyze "query"` | — | Analytics report |
| `watch add-keyword TERM` | — | Subscribe to topic |
| `check-alerts` | — | Fetch new papers |
| `library add ID` | — | Add to library |
| `library list` | — | Browse library |
| `batch FILE` | — | Bulk download |
| `digest` | — | Daily digest |
| `citations ID -i` | — | Citation count |
| `related ID` | — | Similar papers |
| `config show` | — | View settings |

### Common Flags
| Flag | Short | Applies To | Description |
|------|-------|-----------|-------------|
| `--max-results N` | `-n` | search, analyze, export | Number of papers |
| `--preview-only` | `-p` | search, batch | No download |
| `--auto-download` | `-a` | search | Skip confirmation |
| `--download-dir PATH` | `-d` | search, batch | Save location |
| `--categories CAT` | `-c` | search, export, analyze | arXiv category filter |
| `--recent-days N` | — | search | Papers from last N days |
| `--add-to-library` | `-l` | search, batch | Save to local library |
| `--manifest` | `-m` | search | Save a JSON manifest |
| `--is-id` | `-i` | citations | Treat arg as arXiv ID |
| `--is-query` | `-q` | summarize | Treat arg as search query |

---

## 19. BibTeX Management

Import external references or export your entire library:

```bash
# Import papers from a BibTeX file into your library
python main.py library import-bib my_references.bib

# Export your entire library to a BibTeX file
python main.py library export-bib complete_library.bib
```

---

## 20. Advanced Library Features

Modernize your local research database with exports and synchronization:

### Markdown Export (Obsidian/Notion)
```bash
# Export library metadata as individual Markdown files
python main.py library export-md --output-dir ~/MyKnowledgeBase

# Filter by tag before exporting
python main.py library export-md -t "must-read" -d ~/Obsidian/Papers
```

### Metadata Synchronization
```bash
# Update citation counts and venue info for library papers
python main.py library sync-metadata

# Sync a specific paper
python main.py library sync-metadata --id 1706.03762
```

### Keyword Density Analysis
```bash
# Find the most frequent keywords across your library
python main.py library analyze-keywords --limit 30

# Analyze keywords for a specific topic/tag
python main.py library analyze-keywords --tag "NLP"
```

---

## 21. AI Paper Comparison

Use Gemini 1.5 Flash to perform deep comparisons between papers:

```bash
# Basic structural comparison (TF-IDF based)
python main.py compare 1706.03762 2301.07041

# AI-powered deep comparison (requires GOOGLE_API_KEY)
python main.py compare 1706.03762 2301.07041 --ai

# Compare papers from Semantic Scholar
python main.py compare id1 id2 --source semantic_scholar --ai
```

---

## 22. Full-Text PDF Search

Search for text across your entire downloaded PDF collection:

```bash
# Search for a term in all downloaded PDFs
python main.py library search-pdfs "attention mechanism"

# Case-sensitive search
python main.py library search-pdfs "PyTorch" --case-sensitive
```

---

## 23. Webhook Notifications

Get alerts delivered directly to Discord or Slack:

```bash
# Set your webhook URL
python main.py webhook set https://discord.com/api/webhooks/...

# Send a test notification
python main.py webhook test

# New papers found via alerts will now be sent to this webhook
python main.py check-alerts --days 1
```

---

## 24. Search History & Analytics

Persistent tracking of your research activity:

```bash
# View list of recent searches
python main.py history list --limit 10

# View search pattern statistics
python main.py history stats

# Clear search history
python main.py history list --clear
```

---

*Happy researching! 🎓📖*

For more help: `python main.py COMMAND --help`
