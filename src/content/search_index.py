"""
Simple TF-IDF search index for content chunks.
No external dependencies needed -- uses pure Python.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass

from .loader import ContentItem, ContentStore


# Common English stop words to ignore in search
STOP_WORDS = frozenset({
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
    'could', 'should', 'may', 'might', 'shall', 'can', 'this', 'that',
    'these', 'those', 'it', 'its', 'i', 'you', 'he', 'she', 'we', 'they',
    'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their',
    'what', 'which', 'who', 'whom', 'where', 'when', 'why', 'how',
    'not', 'no', 'nor', 'if', 'then', 'than', 'so', 'as', 'up', 'out',
    'about', 'into', 'through', 'during', 'before', 'after', 'above',
    'below', 'between', 'under', 'again', 'further', 'once', 'here',
    'there', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
    'other', 'some', 'such', 'only', 'own', 'same', 'just', 'also',
    'very', 'too', 'quite', 'rather', 'enough',
})


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words, removing stop words."""
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


@dataclass
class IndexedChunk:
    """A chunk of content with its TF-IDF vector."""
    item: ContentItem
    chunk_index: int
    chunk_text: str
    tokens: list[str]
    tf: dict[str, float]  # term frequency


@dataclass
class SearchResult:
    """A single search result."""
    item: ContentItem
    chunk_text: str
    chunk_index: int
    score: float


class SearchIndex:
    """Simple in-memory TF-IDF search index."""

    def __init__(self):
        self.chunks: list[IndexedChunk] = []
        self.df: Counter = Counter()  # document frequency
        self.num_docs: int = 0

    def build(self, store: ContentStore) -> None:
        """Build the index from a ContentStore."""
        self.chunks = []
        self.df = Counter()

        for item in store.all_items:
            for i, chunk_text in enumerate(item.chunks):
                tokens = tokenize(chunk_text)
                if not tokens:
                    continue

                # Calculate term frequency (normalized)
                token_counts = Counter(tokens)
                max_count = max(token_counts.values()) if token_counts else 1
                tf = {t: count / max_count for t, count in token_counts.items()}

                indexed = IndexedChunk(
                    item=item,
                    chunk_index=i,
                    chunk_text=chunk_text,
                    tokens=tokens,
                    tf=tf,
                )
                self.chunks.append(indexed)

                # Update document frequency (count each term once per doc)
                unique_tokens = set(tokens)
                self.df.update(unique_tokens)

        self.num_docs = len(self.chunks)
        print(f"Search index built: {self.num_docs} chunks indexed, "
              f"{len(self.df)} unique terms")

    def search(self, query: str, top_k: int = 5,
               category: str | None = None) -> list[SearchResult]:
        """
        Search for chunks matching the query.

        Args:
            query: Search query string
            top_k: Number of results to return
            category: Optional category filter (articles, glossary, etc.)

        Returns:
            List of SearchResult sorted by relevance score
        """
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        # Calculate IDF for query terms
        idf = {}
        for token in set(query_tokens):
            doc_freq = self.df.get(token, 0)
            if doc_freq > 0:
                idf[token] = math.log(self.num_docs / doc_freq)
            else:
                idf[token] = 0

        # Score each chunk
        results = []
        seen_urls = set()  # deduplicate by URL (take best chunk per article)

        for chunk in self.chunks:
            # Category filter
            if category and chunk.item.category != category:
                continue

            # Calculate TF-IDF cosine-like score
            score = 0.0
            for token in query_tokens:
                if token in chunk.tf:
                    score += chunk.tf[token] * idf.get(token, 0)

            # Boost exact phrase matches
            chunk_lower = chunk.chunk_text.lower()
            query_lower = query.lower()
            if query_lower in chunk_lower:
                score *= 2.0

            # Boost title matches
            title_lower = chunk.item.title.lower()
            for token in query_tokens:
                if token in title_lower:
                    score *= 1.3

            if score > 0:
                results.append(SearchResult(
                    item=chunk.item,
                    chunk_text=chunk.chunk_text,
                    chunk_index=chunk.chunk_index,
                    score=score,
                ))

        # Sort by score descending
        results.sort(key=lambda r: r.score, reverse=True)

        # Deduplicate: keep only the best chunk per URL
        deduped = []
        for result in results:
            if result.item.url not in seen_urls:
                seen_urls.add(result.item.url)
                deduped.append(result)
                if len(deduped) >= top_k:
                    break

        return deduped
