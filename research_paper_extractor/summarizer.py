"""
Abstract summarizer using TF-IDF keyword extraction.
Produces bullet-point key-point summaries from paper abstracts without any AI API.
"""

import re
import math
from typing import List, Tuple, Dict, Any
try:
    from rake_nltk import Rake
    RAKE_AVAILABLE = True
except ImportError:
    RAKE_AVAILABLE = False
from .arxiv_api import ArxivPaper

# Extended stop words for academic text
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'over', 'after',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
    'its', 'it', 'this', 'that', 'these', 'those', 'we', 'our', 'us',
    'also', 'can', 'show', 'shows', 'shown', 'paper', 'propose', 'proposed',
    'present', 'presented', 'work', 'works', 'result', 'results', 'use',
    'used', 'using', 'however', 'thus', 'therefore', 'such', 'which',
    'than', 'more', 'most', 'their', 'they', 'each', 'both', 'well',
    'not', 'one', 'two', 'three', 'new', 'based', 'achieve', 'achieved',
}


def _tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase word tokens."""
    tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [t for t in tokens if t not in STOP_WORDS]


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Split on '. ', '! ', '? '  while handling abbreviations loosely
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 30]


def _compute_tf(tokens: List[str]) -> Dict[str, float]:
    """Compute term frequency."""
    freq: Dict[str, float] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    total = len(tokens) or 1
    return {t: c / total for t, c in freq.items()}


def _compute_idf(documents: List[List[str]]) -> Dict[str, float]:
    """Compute inverse document frequency across sentences."""
    n = len(documents)
    idf: Dict[str, float] = {}
    for doc in documents:
        unique = set(doc)
        for word in unique:
            idf[word] = idf.get(word, 0) + 1
    return {word: math.log(n / (1 + cnt)) for word, cnt in idf.items()}


def extract_keywords(text: str, top_n: int = 8) -> List[Tuple[str, float]]:
    """
    Extract top keywords from text using RAKE or TF-IDF.
    """
    if RAKE_AVAILABLE:
        try:
            r = Rake()
            r.extract_keywords_from_text(text)
            keywords = r.get_ranked_phrases_with_scores()[:top_n]
            # Convert to (word, score) format
            return [(word, score) for score, word in keywords]
        except Exception:
            pass

    # Fallback to TF-IDF
    sentences = _split_sentences(text)
    if not sentences:
        tokens = _tokenize(text)
        from collections import Counter
        return [(w, c) for w, c in Counter(tokens).most_common(top_n)]

    tokenized_sentences = [_tokenize(s) for s in sentences]
    all_tokens = _tokenize(text)
    tf = _compute_tf(all_tokens)
    idf = _compute_idf(tokenized_sentences)

    scores = {word: tf_score * idf.get(word, 1.0) for word, tf_score in tf.items()}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:top_n]


def summarize_abstract(abstract: str, max_sentences: int = 3) -> List[str]:
    """
    Produce a bullet-point summary of an abstract by extractive sentence scoring.

    Args:
        abstract: Full abstract text
        max_sentences: Maximum number of bullet points

    Returns:
        List of selected key sentences
    """
    sentences = _split_sentences(abstract)
    if not sentences:
        return [abstract[:300].strip()]

    if len(sentences) <= max_sentences:
        return sentences

    # Score each sentence by the sum of TF-IDF scores of its tokens
    tokenized_sentences = [_tokenize(s) for s in sentences]
    idf = _compute_idf(tokenized_sentences)
    all_tokens = _tokenize(abstract)
    tf = _compute_tf(all_tokens)

    sentence_scores = []
    for i, (sentence, tokens) in enumerate(zip(sentences, tokenized_sentences)):
        score = sum(tf.get(t, 0) * idf.get(t, 1.0) for t in tokens)
        # Boost first and last sentences (they often contain key info)
        if i == 0:
            score *= 1.5
        if i == len(sentences) - 1:
            score *= 1.2
        sentence_scores.append((score, i, sentence))

    # Select top sentences and restore original order
    top = sorted(sentence_scores, key=lambda x: x[0], reverse=True)[:max_sentences]
    top_sorted = sorted(top, key=lambda x: x[1])
    return [s for _, _, s in top_sorted]


def summarize_paper(paper: ArxivPaper, max_sentences: int = 3, top_keywords: int = 8) -> str:
    """
    Generate a formatted summary of a single paper.

    Args:
        paper: ArxivPaper object
        max_sentences: Max bullet points in summary
        top_keywords: Number of keywords to extract

    Returns:
        Formatted multi-line summary string
    """
    lines = []
    lines.append(f'Title   : {paper.title}')
    lines.append(f'Authors : {", ".join(paper.authors[:4])}{"..." if len(paper.authors) > 4 else ""}')
    lines.append(f'arXiv   : {paper.id}  ({paper.published.strftime("%Y-%m-%d")})')
    lines.append(f'URL     : {paper.abs_url}')
    lines.append('')
    lines.append('Key Points:')
    bullet_points = summarize_abstract(paper.summary, max_sentences=max_sentences)
    for point in bullet_points:
        lines.append(f'  • {point}')
    lines.append('')
    keywords = extract_keywords(paper.summary, top_n=top_keywords)
    kw_str = ', '.join(w for w, _ in keywords)
    lines.append(f'Keywords: {kw_str}')
    return '\n'.join(lines)
