"""
Inverted Index implementation for text search.
Maps words to the documents (URLs) they appear in.
"""

from collections import defaultdict
from typing import Dict, List, Set


class InvertedIndex:
    """
    An inverted index data structure that maps terms to document IDs.
    """

    def __init__(self):
        """Initialize an empty inverted index."""
        self.index: Dict[str, Set[str]] = defaultdict(set)

    def add_document(self, doc_id: str, terms: List[str]) -> None:
        """
        Add a document to the inverted index.

        Args:
            doc_id: Unique identifier for the document (e.g., URL)
            terms: List of terms/words from the document
        """
        for term in terms:
            term_lower = term.lower()
            self.index[term_lower].add(doc_id)

    def search(self, term: str) -> Set[str]:
        """
        Search for documents containing the given term.

        Args:
            term: The search term

        Returns:
            Set of document IDs containing the term
        """
        return self.index.get(term.lower(), set())

    def get_all_terms(self) -> List[str]:
        """
        Get all terms in the index.

        Returns:
            List of all indexed terms
        """
        return sorted(self.index.keys())

    def get_document_count(self, term: str) -> int:
        """
        Get the number of documents containing the term.

        Args:
            term: The search term

        Returns:
            Number of documents containing the term
        """
        return len(self.search(term))
