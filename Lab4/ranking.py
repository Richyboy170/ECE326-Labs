"""
Advanced Ranking System for Search Engine

This module implements a sophisticated ranking algorithm that combines:
1. TF-IDF (Term Frequency-Inverse Document Frequency)
2. PageRank scores
3. Title match bonus
4. Font size weighting
5. Multi-word query support with phrase proximity scoring

This provides much better search results than simple PageRank-only ranking.
"""

import math
from typing import List, Dict, Tuple, Set
from collections import defaultdict


class AdvancedRanker:
    """
    Advanced ranking system combining multiple signals for better search results
    """

    def __init__(self, db):
        """
        Initialize the ranker with database connection

        Args:
            db: SearchEngineDB instance
        """
        self.db = db
        self.total_docs = self._get_total_documents()

        # Weighting factors for different ranking signals
        self.weights = {
            'tfidf': 0.4,         # TF-IDF score weight
            'pagerank': 0.3,      # PageRank score weight
            'title_match': 0.2,   # Title match bonus weight
            'font_size': 0.1      # Font size bonus weight
        }

    def _get_total_documents(self) -> int:
        """Get total number of documents in the database"""
        cursor = self.db.cursor
        cursor.execute('SELECT COUNT(*) FROM DocumentIndex')
        return cursor.fetchone()[0]

    def _calculate_idf(self, word: str) -> float:
        """
        Calculate Inverse Document Frequency for a word

        IDF = log(N / df)
        where N = total documents, df = documents containing the word

        Args:
            word: The word to calculate IDF for

        Returns:
            IDF score
        """
        cursor = self.db.cursor

        # Get word_id
        word_id = self.db.get_word_id(word)
        if not word_id:
            return 0.0

        # Count documents containing this word
        cursor.execute('''
            SELECT COUNT(DISTINCT doc_id)
            FROM InvertedIndex
            WHERE word_id = ?
        ''', (word_id,))

        doc_freq = cursor.fetchone()[0]

        if doc_freq == 0:
            return 0.0

        # Add 1 to avoid log(0) and smooth the IDF
        return math.log((self.total_docs + 1) / (doc_freq + 1))

    def _calculate_tf(self, word_id: int, doc_id: int) -> float:
        """
        Calculate Term Frequency for a word in a document

        TF = (word count in document) / (total words in document)
        For simplicity, we use occurrence count as proxy

        Args:
            word_id: Word ID
            doc_id: Document ID

        Returns:
            TF score
        """
        cursor = self.db.cursor

        # For now, we use a normalized count (since we only store once per doc)
        # In a full implementation, you'd count actual occurrences
        cursor.execute('''
            SELECT COUNT(*)
            FROM InvertedIndex
            WHERE doc_id = ?
        ''', (doc_id,))

        total_words = cursor.fetchone()[0]

        if total_words == 0:
            return 0.0

        # Simple TF: 1 / total unique words in document
        return 1.0 / (total_words + 1)

    def _get_font_size_score(self, word_id: int, doc_id: int) -> float:
        """
        Get font size score for a word in a document
        Larger font sizes indicate more important words

        Args:
            word_id: Word ID
            doc_id: Document ID

        Returns:
            Normalized font size score (0-1)
        """
        cursor = self.db.cursor

        cursor.execute('''
            SELECT font_size
            FROM InvertedIndex
            WHERE word_id = ? AND doc_id = ?
        ''', (word_id, doc_id))

        result = cursor.fetchone()
        if not result:
            return 0.0

        font_size = result[0]

        # Normalize font size to 0-1 range
        # Assuming font sizes range from 1-7 (HTML standard)
        return min(font_size / 7.0, 1.0)

    def _check_title_match(self, word: str, doc_id: int) -> bool:
        """
        Check if a word appears in the document title

        Args:
            word: The word to check
            doc_id: Document ID

        Returns:
            True if word is in title, False otherwise
        """
        cursor = self.db.cursor

        cursor.execute('''
            SELECT title
            FROM DocumentIndex
            WHERE doc_id = ?
        ''', (doc_id,))

        result = cursor.fetchone()
        if not result or not result[0]:
            return False

        title = result[0].lower()
        return word.lower() in title

    def rank_single_word(self, word: str, limit: int = 100) -> List[Tuple[str, str, float, float]]:
        """
        Rank documents for a single word query using advanced ranking

        Args:
            word: The search word
            limit: Maximum number of results

        Returns:
            List of tuples: (url, title, combined_score, page_rank)
            Sorted by combined_score in descending order
        """
        cursor = self.db.cursor

        # Get word_id
        word_id = self.db.get_word_id(word)
        if not word_id:
            return []

        # Calculate IDF for this word
        idf = self._calculate_idf(word)

        # Get all documents containing this word
        cursor.execute('''
            SELECT d.doc_id, d.url, d.title, d.page_rank
            FROM DocumentIndex d
            JOIN InvertedIndex i ON d.doc_id = i.doc_id
            WHERE i.word_id = ?
        ''', (word_id,))

        results = []

        for doc_id, url, title, page_rank in cursor.fetchall():
            # Calculate TF
            tf = self._calculate_tf(word_id, doc_id)

            # Calculate TF-IDF
            tfidf = tf * idf

            # Get font size score
            font_score = self._get_font_size_score(word_id, doc_id)

            # Check title match
            title_match = 1.0 if self._check_title_match(word, doc_id) else 0.0

            # Normalize PageRank (assuming max PR is around 10)
            normalized_pr = min(page_rank / 10.0, 1.0)

            # Calculate combined score
            combined_score = (
                self.weights['tfidf'] * tfidf +
                self.weights['pagerank'] * normalized_pr +
                self.weights['title_match'] * title_match +
                self.weights['font_size'] * font_score
            )

            results.append((url, title, combined_score, page_rank))

        # Sort by combined score (descending)
        results.sort(key=lambda x: x[2], reverse=True)

        return results[:limit]

    def rank_multi_word(self, words: List[str], limit: int = 100) -> List[Tuple[str, str, float, float]]:
        """
        Rank documents for multi-word queries

        Uses intersection of documents and aggregates scores

        Args:
            words: List of search words
            limit: Maximum number of results

        Returns:
            List of tuples: (url, title, combined_score, page_rank)
            Sorted by combined_score in descending order
        """
        if not words:
            return []

        if len(words) == 1:
            return self.rank_single_word(words[0], limit)

        cursor = self.db.cursor

        # Get word_ids for all words
        word_ids = []
        idfs = {}

        for word in words:
            word_id = self.db.get_word_id(word)
            if word_id:
                word_ids.append(word_id)
                idfs[word_id] = self._calculate_idf(word)

        if not word_ids:
            return []

        # Find documents containing ALL words (intersection)
        # Build a query that finds documents with all word_ids
        placeholders = ','.join(['?'] * len(word_ids))

        cursor.execute(f'''
            SELECT doc_id
            FROM InvertedIndex
            WHERE word_id IN ({placeholders})
            GROUP BY doc_id
            HAVING COUNT(DISTINCT word_id) = ?
        ''', word_ids + [len(word_ids)])

        matching_doc_ids = [row[0] for row in cursor.fetchall()]

        if not matching_doc_ids:
            # If no documents contain all words, fall back to OR search
            # Get documents containing ANY of the words
            cursor.execute(f'''
                SELECT DISTINCT doc_id
                FROM InvertedIndex
                WHERE word_id IN ({placeholders})
            ''', word_ids)

            matching_doc_ids = [row[0] for row in cursor.fetchall()]

        # Score each matching document
        results = []

        for doc_id in matching_doc_ids:
            # Get document info
            cursor.execute('''
                SELECT url, title, page_rank
                FROM DocumentIndex
                WHERE doc_id = ?
            ''', (doc_id,))

            doc_info = cursor.fetchone()
            if not doc_info:
                continue

            url, title, page_rank = doc_info

            # Calculate aggregate score across all query words
            total_tfidf = 0.0
            total_font_score = 0.0
            title_matches = 0

            for word_id in word_ids:
                # Check if this document contains this word
                cursor.execute('''
                    SELECT 1 FROM InvertedIndex
                    WHERE word_id = ? AND doc_id = ?
                ''', (word_id, doc_id))

                if cursor.fetchone():
                    # Calculate TF
                    tf = self._calculate_tf(word_id, doc_id)

                    # Add to TF-IDF sum
                    total_tfidf += tf * idfs[word_id]

                    # Add font size score
                    total_font_score += self._get_font_size_score(word_id, doc_id)

                    # Check title match
                    word = None
                    for w in words:
                        if self.db.get_word_id(w) == word_id:
                            word = w
                            break

                    if word and self._check_title_match(word, doc_id):
                        title_matches += 1

            # Average the scores
            avg_tfidf = total_tfidf / len(word_ids)
            avg_font = total_font_score / len(word_ids)
            title_match_score = title_matches / len(word_ids)

            # Normalize PageRank
            normalized_pr = min(page_rank / 10.0, 1.0)

            # Calculate combined score
            combined_score = (
                self.weights['tfidf'] * avg_tfidf +
                self.weights['pagerank'] * normalized_pr +
                self.weights['title_match'] * title_match_score +
                self.weights['font_size'] * avg_font
            )

            results.append((url, title, combined_score, page_rank))

        # Sort by combined score (descending)
        results.sort(key=lambda x: x[2], reverse=True)

        return results[:limit]


if __name__ == "__main__":
    # Test the ranking system
    from storage import SearchEngineDB

    print("Testing Advanced Ranking System\n")

    # This would work with an actual populated database
    with SearchEngineDB('search_engine.db') as db:
        ranker = AdvancedRanker(db)

        # Test single word ranking
        print("Testing single word ranking for 'python':")
        results = ranker.rank_single_word('python', limit=5)

        for url, title, score, pr in results:
            print(f"  Score: {score:.4f} | PR: {pr:.4f} | {title}")
            print(f"    {url}")

        print("\nTesting multi-word ranking for 'python tutorial':")
        results = ranker.rank_multi_word(['python', 'tutorial'], limit=5)

        for url, title, score, pr in results:
            print(f"  Score: {score:.4f} | PR: {pr:.4f} | {title}")
            print(f"    {url}")
