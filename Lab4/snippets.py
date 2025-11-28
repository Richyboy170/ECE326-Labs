"""
Search Result Snippet Generation

This module generates contextual snippets for search results.
Snippets show the query terms in context, helping users determine relevance.

Features:
- Context extraction around query terms
- Highlighting of query terms
- Smart truncation with ellipsis
- Multi-word query support
"""

import re
from typing import List, Tuple, Optional


class SnippetGenerator:
    """
    Generates contextual snippets for search results
    """

    def __init__(self, max_snippet_length: int = 200, context_words: int = 10):
        """
        Initialize snippet generator

        Args:
            max_snippet_length: Maximum snippet length in characters
            context_words: Number of words to show on each side of match
        """
        self.max_snippet_length = max_snippet_length
        self.context_words = context_words

    def generate_snippet(self, text: str, query_words: List[str]) -> str:
        """
        Generate a snippet from text highlighting query words

        Args:
            text: Full text to extract snippet from
            query_words: List of query words to highlight

        Returns:
            Generated snippet with highlighted query terms
        """
        if not text or not query_words:
            return self._truncate(text or "")

        # Clean and normalize
        text = self._clean_text(text)
        query_words_lower = [w.lower() for w in query_words]

        # Find best position to extract snippet (where most query words appear)
        best_position = self._find_best_position(text, query_words_lower)

        if best_position is None:
            # No query words found, return beginning
            return self._truncate(text)

        # Extract context around best position
        snippet = self._extract_context(text, best_position, query_words_lower)

        # Highlight query words
        snippet = self._highlight_words(snippet, query_words_lower)

        return snippet

    def generate_snippet_from_html(self, html: str, query_words: List[str]) -> str:
        """
        Generate snippet from HTML content

        Args:
            html: HTML content
            query_words: Query words to highlight

        Returns:
            Generated snippet
        """
        # Strip HTML tags
        text = self._strip_html(html)
        return self.generate_snippet(text, query_words)

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _strip_html(self, html: str) -> str:
        """Strip HTML tags from text"""
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)

        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')

        return text

    def _find_best_position(self, text: str, query_words: List[str]) -> Optional[int]:
        """
        Find the best position in text where most query words appear

        Args:
            text: Text to search
            query_words: Query words (lowercase)

        Returns:
            Position index or None
        """
        text_lower = text.lower()
        words = text_lower.split()

        if not words:
            return None

        # Score each position by number of query words nearby
        best_score = 0
        best_position = 0

        for i, word in enumerate(words):
            # Count matching query words in window
            window_start = max(0, i - self.context_words)
            window_end = min(len(words), i + self.context_words + 1)
            window_words = words[window_start:window_end]

            score = sum(1 for qw in query_words if any(qw in w for w in window_words))

            if score > best_score:
                best_score = score
                # Convert word position to character position
                best_position = len(' '.join(words[:i]))

        if best_score == 0:
            return None

        return best_position

    def _extract_context(self, text: str, position: int, query_words: List[str]) -> str:
        """
        Extract context around position

        Args:
            text: Full text
            position: Position to center on
            query_words: Query words for context expansion

        Returns:
            Extracted context
        """
        # Get window around position
        start = max(0, position - self.max_snippet_length // 2)
        end = min(len(text), start + self.max_snippet_length)

        # Adjust start if we're at the end
        if end == len(text):
            start = max(0, end - self.max_snippet_length)

        snippet = text[start:end]

        # Try to break at word boundaries
        if start > 0:
            # Find first space
            first_space = snippet.find(' ')
            if first_space > 0 and first_space < 50:
                snippet = snippet[first_space + 1:]
                snippet = '...' + snippet

        if end < len(text):
            # Find last space
            last_space = snippet.rfind(' ')
            if last_space > len(snippet) - 50:
                snippet = snippet[:last_space]
                snippet = snippet + '...'

        return snippet.strip()

    def _highlight_words(self, text: str, query_words: List[str]) -> str:
        """
        Highlight query words in text

        Args:
            text: Text to highlight
            query_words: Words to highlight (lowercase)

        Returns:
            Text with highlighted words
        """
        # Use <b> tags for highlighting
        highlighted = text

        for word in query_words:
            # Create case-insensitive pattern that matches whole words
            pattern = re.compile(r'\b(' + re.escape(word) + r'\w*)\b', re.IGNORECASE)
            highlighted = pattern.sub(r'<b>\1</b>', highlighted)

        return highlighted

    def _truncate(self, text: str) -> str:
        """
        Truncate text to max length

        Args:
            text: Text to truncate

        Returns:
            Truncated text
        """
        if len(text) <= self.max_snippet_length:
            return text

        # Truncate at word boundary
        truncated = text[:self.max_snippet_length]
        last_space = truncated.rfind(' ')

        if last_space > 0:
            truncated = truncated[:last_space]

        return truncated + '...'


class SnippetCache:
    """
    Cache for generated snippets to avoid regeneration
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize snippet cache

        Args:
            max_size: Maximum number of snippets to cache
        """
        self.cache = {}
        self.max_size = max_size

    def _make_key(self, doc_id: int, query: str) -> str:
        """Create cache key"""
        return f"{doc_id}:{query.lower()}"

    def get(self, doc_id: int, query: str) -> Optional[str]:
        """Get cached snippet"""
        key = self._make_key(doc_id, query)
        return self.cache.get(key)

    def put(self, doc_id: int, query: str, snippet: str):
        """Cache a snippet"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            self.cache.pop(next(iter(self.cache)))

        key = self._make_key(doc_id, query)
        self.cache[key] = snippet

    def clear(self):
        """Clear cache"""
        self.cache.clear()


# Global snippet generator
_snippet_generator = None
_snippet_cache = None


def get_snippet_generator() -> SnippetGenerator:
    """Get global snippet generator instance"""
    global _snippet_generator
    if _snippet_generator is None:
        _snippet_generator = SnippetGenerator()
    return _snippet_generator


def get_snippet_cache() -> SnippetCache:
    """Get global snippet cache instance"""
    global _snippet_cache
    if _snippet_cache is None:
        _snippet_cache = SnippetCache()
    return _snippet_cache


if __name__ == "__main__":
    # Test snippet generation
    print("Testing Snippet Generator\n")

    generator = SnippetGenerator(max_snippet_length=150, context_words=8)

    # Test text
    text = """
    Python is a high-level, interpreted programming language with dynamic semantics.
    Its high-level built-in data structures, combined with dynamic typing and dynamic binding,
    make it very attractive for Rapid Application Development, as well as for use as a
    scripting or glue language to connect existing components together. Python's simple,
    easy to learn syntax emphasizes readability and therefore reduces the cost of program
    maintenance. Python supports modules and packages, which encourages program modularity
    and code reuse.
    """

    # Test 1: Single word query
    print("Test 1: Query 'python'")
    snippet = generator.generate_snippet(text, ['python'])
    print(f"Snippet: {snippet}\n")

    # Test 2: Multi-word query
    print("Test 2: Query 'python programming language'")
    snippet = generator.generate_snippet(text, ['python', 'programming', 'language'])
    print(f"Snippet: {snippet}\n")

    # Test 3: Query not in text
    print("Test 3: Query 'java' (not in text)")
    snippet = generator.generate_snippet(text, ['java'])
    print(f"Snippet: {snippet}\n")

    # Test 4: HTML stripping
    html = """
    <html>
    <head><title>Python Tutorial</title></head>
    <body>
    <h1>Learn Python Programming</h1>
    <p>Python is an amazing <b>programming language</b> used for web development,
    data science, and automation.</p>
    </body>
    </html>
    """

    print("Test 4: HTML content with query 'python programming'")
    snippet = generator.generate_snippet_from_html(html, ['python', 'programming'])
    print(f"Snippet: {snippet}\n")
