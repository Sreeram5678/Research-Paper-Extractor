#  Research Paper Downloader - Usage Examples

A comprehensive guide to using the arXiv Research Paper Downloader with automatic topic-based folder organization.

##  Quick Start

```bash
# Activate virtual environment
source rp/bin/activate

# Basic search
python main.py search "machine learning"

# Preview results without downloading
python main.py search "deep learning" --preview-only

# Auto-download without confirmation
python main.py search "neural networks" --auto-download
```

---

##  Table of Contents

1. [Basic Search Commands](#1-basic-search-commands)
2. [Search by Author](#2-search-by-author-commands)
3. [Download by ID](#3-download-by-id-commands)
4. [Interactive Mode](#4-interactive-mode)
5. [Utility Commands](#5-utility-commands)
6. [Advanced Examples](#6-advanced-examples)
7. [Folder Organization](#7-folder-organization)
8. [Pro Tips](#8-pro-tips)

---

## 1. 🔍 Basic Search Commands

### Simple Search
```bash
# Basic search (creates folder: downloads/machine_learning/)
python main.py search "machine learning"

# Other topic examples
python main.py search "deep learning"
python main.py search "computer vision"
python main.py search "natural language processing"
python main.py search "reinforcement learning"
```

### Control Number of Results
```bash
# Limit results
python main.py search "neural networks" --max-results 5
python main.py search "quantum computing" -n 3

# Get more results
python main.py search "artificial intelligence" --max-results 20
```

### Preview Mode (No Downloads)
```bash
# Preview only - see results without downloading
python main.py search "blockchain" --preview-only
python main.py search "cybersecurity" -p
```

### Auto-Download Mode
```bash
# Download all results without confirmation
python main.py search "robotics" --auto-download
python main.py search "bioinformatics" -a
```

### Category Filtering
```bash
# Single category
python main.py search "machine learning" --categories cs.LG

# Multiple categories
python main.py search "AI research" -c cs.AI -c cs.LG -c cs.CV

# Available categories: cs.AI, cs.LG, cs.CV, cs.CL, cs.NE, stat.ML, etc.
python main.py categories  # See full list
```

### Sort Options
```bash
# Sort by relevance (default)
python main.py search "transformers" --sort-by relevance

# Sort by date
python main.py search "GPT models" --sort-by lastUpdatedDate
python main.py search "BERT" --sort-by submittedDate
```

### Recent Papers Only
```bash
# Papers from last 7 days
python main.py search "ChatGPT" --recent-days 7

# Papers from last month
python main.py search "large language models" --recent-days 30
```

### Custom Download Directory
```bash
# Specify custom directory
python main.py search "federated learning" --download-dir ~/Research/Papers
python main.py search "edge computing" -d /path/to/custom/directory
```

### Combined Options
```bash
# Complex search with multiple options
python main.py search "graph neural networks" \
  --max-results 10 \
  --categories cs.LG cs.AI \
  --sort-by lastUpdatedDate \
  --recent-days 30 \
  --auto-download
```

---

## 2. 👤 Search by Author Commands

### Basic Author Search
```bash
# Search by author (creates folder: downloads/author_geoffrey_hinton/)
python main.py search-by-author "Geoffrey Hinton"
python main.py search-by-author "Yann LeCun"
python main.py search-by-author "Andrew Ng"
python main.py search-by-author "Ian Goodfellow"
```

### Author Search with Options
```bash
# Limit results for prolific authors
python main.py search-by-author "Yoshua Bengio" --max-results 5

# Preview author's papers
python main.py search-by-author "Fei-Fei Li" --preview-only

# Get many papers from an author
python main.py search-by-author "Jürgen Schmidhuber" -n 20
```

### Custom Directory for Author Papers
```bash
# Organize by research group
python main.py search-by-author "Pieter Abbeel" -d ~/Research/Berkeley_AI
python main.py search-by-author "Demis Hassabis" -d ~/Research/DeepMind
```

---

## 3. 📄 Download by ID Commands

### Basic Paper Download
```bash
# Download specific papers (creates folder: downloads/paper_ID/)
python main.py download-by-id "1706.03762"  # Attention Is All You Need
python main.py download-by-id "2301.07041"  # Example arXiv ID
python main.py download-by-id "1412.6980"   # Adam optimizer paper
```

### Custom Filename
```bash
# Rename downloaded file
python main.py download-by-id "1706.03762" --filename "attention_mechanism"
python main.py download-by-id "2301.07041" -f "my_research_paper"
```

### Custom Directory
```bash
# Download to specific location
python main.py download-by-id "1706.03762" -d ~/Important_Papers
```

---

## 4. 🎮 Interactive Mode

### Start Interactive Session
```bash
# Interactive mode (creates folder: downloads/interactive_QUERY/)
python main.py interactive --query "transformers"
python main.py interactive -q "machine learning"
```

### Interactive with Custom Settings
```bash
# Set max results and directory
python main.py interactive -q "deep learning" -n 15 -d ~/Research
```

### Interactive Workflow
```bash
# Start interactive mode
python main.py interactive -q "neural networks"

# Then follow prompts:
# - View numbered list of papers
# - Type 'all' to download all
# - Type '1,3,5' to download specific papers
# - Type 'new' to search different topic
# - Type 'none' to skip downloads
```

---

## 5. 🛠️ Utility Commands

### List Available Categories
```bash
# See all arXiv categories
python main.py categories
```

### Version Information
```bash
# Check version
python main.py --version
```

### Help Information
```bash
# General help
python main.py --help

# Command-specific help
python main.py search --help
python main.py search-by-author --help
python main.py download-by-id --help
python main.py interactive --help
```

---

## 6. 🎯 Advanced Examples

### Research Workflow Example
```bash
# 1. Preview papers in a field
python main.py search "federated learning" --preview-only

# 2. Download promising papers
python main.py search "federated learning" --max-results 5 --auto-download

# 3. Get papers from key researchers
python main.py search-by-author "Peter Kairouz" --max-results 3

# 4. Download seminal papers
python main.py download-by-id "1602.05629"  # Federated Learning paper
```

### Survey Multiple Topics
```bash
# Quick survey of related fields
python main.py search "computer vision" -n 3 -p
python main.py search "natural language processing" -n 3 -p
python main.py search "speech recognition" -n 3 -p
```

### Build Research Collection
```bash
# Download comprehensive collection
python main.py search "transformer architecture" -n 10 -a
python main.py search "attention mechanisms" -n 8 -a
python main.py search "BERT variations" -n 5 -a
```

### Recent Developments Tracking
```bash
# Track latest developments
python main.py search "large language models" --recent-days 7 -n 5
python main.py search "GPT-4" --recent-days 14 -n 3
python main.py search "multimodal AI" --recent-days 30 -n 10
```

---

## 7. 📁 Folder Organization

### Automatic Folder Creation
Every search automatically creates organized folders:

```
downloads/
├── machine_learning/              # search "machine learning"
├── deep_learning/                 # search "deep learning"
├── computer_vision/               # search "computer vision"
├── natural_language_processing/   # search "natural language processing"
├── author_geoffrey_hinton/        # search-by-author "Geoffrey Hinton"
├── author_yann_lecun/            # search-by-author "Yann LeCun"
├── paper_1706.03762/             # download-by-id "1706.03762"
├── paper_2301.07041/             # download-by-id "2301.07041"
├── interactive_transformers/      # interactive mode with "transformers"
└── federated_learning/           # search "federated learning"
```

### Folder Naming Rules
- Spaces become underscores: `"machine learning"` → `machine_learning/`
- Special characters removed: `"AI & ML"` → `ai_ml/`
- Lowercase conversion: `"Deep Learning"` → `deep_learning/`
- Length limited to 50 characters
- Author searches prefixed: `"John Doe"` → `author_john_doe/`
- Paper IDs prefixed: `"1234.5678"` → `paper_1234.5678/`

---

## 8. 💡 Pro Tips

### Efficiency Tips
```bash
# Use preview to filter before downloading
python main.py search "broad topic" -p
# Then search with specific terms based on preview

# Combine recent and category filters for focused search
python main.py search "AI safety" -c cs.AI --recent-days 30 -n 5
```

### Organization Strategies
```bash
# Create themed collections
python main.py search "computer vision basics" -d ~/Learning/CV_Fundamentals
python main.py search "advanced CV techniques" -d ~/Learning/CV_Advanced

# Separate by research phase
python main.py search "background reading" -d ~/Research/Literature_Review
python main.py search "methodology papers" -d ~/Research/Methods
```

### Batch Operations
```bash
# Use auto-download for known good queries
python main.py search "survey papers machine learning" -a
python main.py search "tutorial deep learning" -a

# Chain commands for comprehensive coverage
python main.py search "topic A" -n 5 -a && \
python main.py search "topic B" -n 5 -a && \
python main.py search "topic C" -n 5 -a
```

### Quality Control
```bash
# Start with small numbers and preview
python main.py search "new research area" -n 3 -p

# Use recent-days to get cutting-edge work
python main.py search "emerging technology" --recent-days 7

# Focus on specific venues with categories
python main.py search "conference papers" -c cs.LG -c cs.AI
```

---

## 🔗 Quick Reference

| Command Pattern | Example | Creates Folder |
|----------------|---------|----------------|
| `search "topic"` | `search "ML"` | `downloads/ml/` |
| `search-by-author "name"` | `search-by-author "Hinton"` | `downloads/author_hinton/` |
| `download-by-id "ID"` | `download-by-id "1706.03762"` | `downloads/paper_1706.03762/` |
| `interactive -q "topic"` | `interactive -q "AI"` | `downloads/interactive_ai/` |

### Common Flags
- `-n, --max-results NUMBER` - Limit number of results
- `-p, --preview-only` - Show results without downloading
- `-a, --auto-download` - Download without confirmation
- `-d, --download-dir PATH` - Custom download directory
- `-c, --categories CAT` - Filter by arXiv category
- `--recent-days NUMBER` - Only recent papers
- `--sort-by TYPE` - Sort results (relevance/date)

---

## 📞 Need Help?

```bash
# Get help for any command
python main.py --help
python main.py COMMAND --help

# List available categories
python main.py categories

# Check version
python main.py --version
```

---

*Happy researching! 🎓📖*
