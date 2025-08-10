# Research Paper Extractor

A Python tool that automatically downloads research papers from arXiv based on topics you specify. Search by keywords, authors, categories, or specific paper IDs and download PDFs with ease!

## Features

- **Smart Search**: Search papers by keywords, topics, or phrases
- **Author Search**: Find all papers by specific researchers
- **Category Filtering**: Filter by arXiv categories (AI, ML, Computer Vision, etc.)
- **Recent Papers**: Find papers published in the last N days
- **Batch Download**: Download multiple papers at once
- **Specific Downloads**: Download papers by arXiv ID
- **Preview Mode**: See search results before downloading
- **Interactive Mode**: User-friendly interactive interface
- **Auto-Organization**: Automatic topic-based folder creation and file naming
- **Topic Folders**: Each search creates its own organized folder

## Installation

1. **Clone or download** this project to your computer
2. **Navigate** to the project directory:
   ```bash
   cd "Research Paper Extractor"
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Basic Search and Download
```bash
# Search for machine learning papers and download them
python main.py search "machine learning" --max-results 5

# Preview results without downloading
python main.py search "neural networks" --preview-only

# Auto-download without confirmation
python main.py search "computer vision" --auto-download
```

### Download by arXiv ID
```bash
# Download a specific paper by its arXiv ID
python main.py download-by-id 2301.07041
```

### Search by Author
```bash
# Find papers by a specific researcher
python main.py search-by-author "Geoffrey Hinton"
```

### Interactive Mode (Recommended for beginners)
```bash
# Launch interactive mode for guided searching
python main.py interactive
```

## Usage Examples

### 1. Search with Category Filters
```bash
# Search for AI papers in specific categories
python main.py search "artificial intelligence" \
  --categories cs.AI \
  --categories cs.LG \
  --max-results 10
```

### 2. Find Recent Papers
```bash
# Find papers from the last 7 days
python main.py search "deep learning" \
  --recent-days 7 \
  --max-results 5
```

### 3. Custom Download Directory
```bash
# Download to a specific folder
python main.py search "robotics" \
  --download-dir "/path/to/my/papers" \
  --max-results 3
```

### 4. Sort Results
```bash
# Sort by publication date (newest first)
python main.py search "nlp" \
  --sort-by submittedDate \
  --max-results 5
```

## Available Commands

### `search` - Main search command
Search and download papers by topic/keywords.

**Options:**
- `--max-results, -n`: Number of papers to find (default: 10)
- `--download-dir, -d`: Download directory (default: ./downloads)
- `--categories, -c`: arXiv categories to search in
- `--sort-by`: Sort by relevance, lastUpdatedDate, or submittedDate
- `--preview-only, -p`: Only show results, don't download
- `--auto-download, -a`: Download all without asking
- `--recent-days`: Only show papers from last N days

### `download-by-id` - Download specific paper
Download a paper using its arXiv ID.

**Options:**
- `--download-dir, -d`: Download directory
- `--filename, -f`: Custom filename

### `search-by-author` - Author search
Find papers by a specific author.

**Options:**
- `--max-results, -n`: Number of papers to find
- `--download-dir, -d`: Download directory
- `--preview-only, -p`: Only preview results

### `categories` - List categories
Show all available arXiv categories.

### `interactive` - Interactive mode
Launch guided interface for easy searching.

## arXiv Categories

Common categories you can use with `--categories`:

| Category | Description |
|----------|-------------|
| `cs.AI` | Artificial Intelligence |
| `cs.LG` | Machine Learning |
| `cs.CV` | Computer Vision and Pattern Recognition |
| `cs.CL` | Computation and Language (NLP) |
| `cs.NE` | Neural and Evolutionary Computing |
| `stat.ML` | Machine Learning (Statistics) |
| `cs.CR` | Cryptography and Security |
| `cs.DB` | Databases |
| `cs.IR` | Information Retrieval |
| `cs.SE` | Software Engineering |

See all categories: `python main.py categories`

## Configuration

You can modify settings in `config.py`:

- **Download directory**: Change `DEFAULT_DOWNLOAD_DIR`
- **Request delay**: Adjust `REQUEST_DELAY` (be respectful to arXiv servers!)
- **Max results**: Change `DEFAULT_MAX_RESULTS`
- **File naming**: Modify `sanitize_filename()` function

## File Organization

**NEW!** Each search topic automatically creates its own organized folder:
```
downloads/
├── machine_learning/
│   ├── Neural_Networks_2301.07041.pdf
│   └── Deep_Learning_Basics_2302.12345.pdf
├── computer_vision/
│   ├── Image_Recognition_2303.67890.pdf
│   └── Object_Detection_2304.11111.pdf
├── author_geoffrey_hinton/
│   └── Hinton_Research_2305.22222.pdf
└── paper_1706.03762/
    └── Attention_Is_All_You_Need_1706.03762.pdf
```

## Tips & Best Practices

1. **Start with preview mode** (`-p`) to see what you'll get before downloading
2. **Use specific keywords** for better results
3. **Combine categories** to narrow down search scope
4. **Be respectful** - don't download hundreds of papers at once
5. **Check recent papers** using `--recent-days` for cutting-edge research
6. **Use interactive mode** if you're new to the tool

## Troubleshooting

### Common Issues

**"No papers found"**
- Try broader keywords
- Check spelling
- Remove category filters and search again

**"Download failed"**
- Check internet connection
- Some papers might not have PDFs available
- Try again later (temporary server issues)

**"Permission denied"**
- Check write permissions in download directory
- Try a different download directory

### Error Logs
The tool provides detailed logging. Check the console output for specific error messages.

## Dependencies

- `requests` - HTTP requests
- `feedparser` - Parse arXiv API responses
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML processing
- `tqdm` - Progress bars
- `click` - Command-line interface
- `python-dateutil` - Date handling

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source. Use it responsibly and respect arXiv's terms of service.

## Complete Usage Guide

For comprehensive usage examples and advanced features, see: **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)**

This detailed guide includes:
- All command examples with explanations
- Advanced usage patterns
- Research workflow examples
- Pro tips and best practices

---

**Happy researching!**

For more help: `python main.py --help` or `python main.py [command] --help`

## Author

**Name**: Sreeram  
**Email**: sreeram.lagisetty@gmail.com  
**GitHub**: [Sreeram5678](https://github.com/Sreeram5678)  
**Instagram**: [@sreeram_3012](https://www.instagram.com/sreeram_3012?igsh=N2Fub3A5eWF4cjJs&utm_source=qr)

## License

This project is open source and available under the [Open Source License](LICENSE). Feel free to use, modify, and distribute this software according to the terms of the license.

---

**Repository**: [Research Paper Extractor](https://github.com/Sreeram5678/Research-Paper-Extractor.git)
