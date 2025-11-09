"""
Persistent Storage Module for Search Engine

This module provides an interface to store and retrieve search engine data
using SQLite database. It stores:
- Lexicon (word_id -> word)
- Document Index (doc_id -> URL, title, PageRank)
- Inverted Index (word_id -> list of (doc_id, font_size))
- Link Graph (from_doc_id -> to_doc_id)
"""

import sqlite3
import json
from typing import Dict, List, Tuple, Set, Optional


class SearchEngineDB:
    """Database interface for search engine persistent storage"""

    def __init__(self, db_file='search_engine.db'):
        """
        Initialize database connection and create tables if they don't exist

        Args:
            db_file: Path to SQLite database file
        """
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist"""

        # Lexicon: stores word -> word_id mapping
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Lexicon (
                word_id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL
            )
        ''')

        # Document Index: stores URL -> doc_id, title, PageRank
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS DocumentIndex (
                doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                page_rank REAL DEFAULT 1.0
            )
        ''')

        # Inverted Index: stores word_id -> list of (doc_id, font_size)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS InvertedIndex (
                word_id INTEGER,
                doc_id INTEGER,
                font_size INTEGER,
                PRIMARY KEY (word_id, doc_id),
                FOREIGN KEY (word_id) REFERENCES Lexicon(word_id),
                FOREIGN KEY (doc_id) REFERENCES DocumentIndex(doc_id)
            )
        ''')

        # Link Graph: stores links between documents
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS LinkGraph (
                from_doc_id INTEGER,
                to_doc_id INTEGER,
                PRIMARY KEY (from_doc_id, to_doc_id),
                FOREIGN KEY (from_doc_id) REFERENCES DocumentIndex(doc_id),
                FOREIGN KEY (to_doc_id) REFERENCES DocumentIndex(doc_id)
            )
        ''')

        # Create indexes for faster queries
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_lexicon_word ON Lexicon(word)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_inverted_word ON InvertedIndex(word_id)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_inverted_doc ON InvertedIndex(doc_id)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_link_from ON LinkGraph(from_doc_id)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_link_to ON LinkGraph(to_doc_id)
        ''')

        self.conn.commit()

    def insert_word(self, word: str) -> int:
        """
        Insert a word into the lexicon and return its word_id

        Args:
            word: The word to insert

        Returns:
            word_id of the inserted or existing word
        """
        try:
            self.cursor.execute('INSERT INTO Lexicon (word) VALUES (?)', (word,))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Word already exists, get its ID
            self.cursor.execute('SELECT word_id FROM Lexicon WHERE word = ?', (word,))
            return self.cursor.fetchone()[0]

    def insert_document(self, url: str, title: str = '') -> int:
        """
        Insert a document into the index and return its doc_id

        Args:
            url: The URL of the document
            title: The title of the document

        Returns:
            doc_id of the inserted or existing document
        """
        try:
            self.cursor.execute('INSERT INTO DocumentIndex (url, title) VALUES (?, ?)',
                                (url, title))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Document already exists, get its ID
            self.cursor.execute('SELECT doc_id FROM DocumentIndex WHERE url = ?', (url,))
            return self.cursor.fetchone()[0]

    def update_document_title(self, doc_id: int, title: str):
        """Update the title of a document"""
        self.cursor.execute('UPDATE DocumentIndex SET title = ? WHERE doc_id = ?',
                            (title, doc_id))
        self.conn.commit()

    def insert_inverted_index(self, word_id: int, doc_id: int, font_size: int):
        """
        Insert an entry into the inverted index

        Args:
            word_id: ID of the word
            doc_id: ID of the document
            font_size: Font size of the word in the document
        """
        try:
            self.cursor.execute('''
                INSERT INTO InvertedIndex (word_id, doc_id, font_size)
                VALUES (?, ?, ?)
            ''', (word_id, doc_id, font_size))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # Entry already exists, update font_size
            self.cursor.execute('''
                UPDATE InvertedIndex SET font_size = ?
                WHERE word_id = ? AND doc_id = ?
            ''', (font_size, word_id, doc_id))
            self.conn.commit()

    def insert_link(self, from_doc_id: int, to_doc_id: int):
        """
        Insert a link between two documents

        Args:
            from_doc_id: Source document ID
            to_doc_id: Target document ID
        """
        try:
            self.cursor.execute('''
                INSERT INTO LinkGraph (from_doc_id, to_doc_id)
                VALUES (?, ?)
            ''', (from_doc_id, to_doc_id))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # Link already exists, ignore
            pass

    def get_word_id(self, word: str) -> Optional[int]:
        """Get the word_id for a given word"""
        self.cursor.execute('SELECT word_id FROM Lexicon WHERE word = ?', (word,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_doc_id(self, url: str) -> Optional[int]:
        """Get the doc_id for a given URL"""
        self.cursor.execute('SELECT doc_id FROM DocumentIndex WHERE url = ?', (url,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def search_word(self, word: str, limit: int = 100, offset: int = 0) -> List[Tuple[str, str, float]]:
        """
        Search for documents containing a word, sorted by PageRank

        Args:
            word: The word to search for
            limit: Maximum number of results to return

        Returns:
            List of tuples: (url, title, page_rank)
        """
        self.cursor.execute('''
            SELECT d.url, d.title, d.page_rank
            FROM DocumentIndex d
            JOIN InvertedIndex i ON d.doc_id = i.doc_id
            JOIN Lexicon l ON i.word_id = l.word_id
            WHERE l.word = ?
            ORDER BY d.page_rank DESC
            LIMIT ? OFFSET ?
        ''', (word, limit, offset))
        return self.cursor.fetchall()

    def get_link_graph(self) -> Dict[int, List[int]]:
        """
        Get the complete link graph for PageRank computation

        Returns:
            Dictionary mapping from_doc_id -> list of to_doc_ids
        """
        self.cursor.execute('SELECT from_doc_id, to_doc_id FROM LinkGraph')
        links = {}
        for from_id, to_id in self.cursor.fetchall():
            if from_id not in links:
                links[from_id] = []
            links[from_id].append(to_id)
        return links

    def update_page_ranks(self, page_ranks: Dict[int, float]):
        """
        Update PageRank scores for all documents

        Args:
            page_ranks: Dictionary mapping doc_id -> PageRank score
        """
        for doc_id, rank in page_ranks.items():
            self.cursor.execute('''
                UPDATE DocumentIndex SET page_rank = ? WHERE doc_id = ?
            ''', (rank, doc_id))
        self.conn.commit()

    def get_all_documents(self) -> List[Tuple[int, str, str, float]]:
        """
        Get all documents in the index

        Returns:
            List of tuples: (doc_id, url, title, page_rank)
        """
        self.cursor.execute('SELECT doc_id, url, title, page_rank FROM DocumentIndex')
        return self.cursor.fetchall()

    def get_statistics(self) -> Dict[str, int]:
        """Get database statistics"""
        stats = {}

        self.cursor.execute('SELECT COUNT(*) FROM Lexicon')
        stats['total_words'] = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM DocumentIndex')
        stats['total_documents'] = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM InvertedIndex')
        stats['total_index_entries'] = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM LinkGraph')
        stats['total_links'] = self.cursor.fetchone()[0]

        return stats

    def close(self):
        """Close the database connection"""
        self.conn.commit()
        self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


if __name__ == "__main__":
    # Test the database module
    print("Testing SearchEngineDB\n")

    # Create a test database
    with SearchEngineDB('test_search.db') as db:
        # Insert some test data
        word1_id = db.insert_word("python")
        word2_id = db.insert_word("programming")
        word3_id = db.insert_word("tutorial")

        doc1_id = db.insert_document("http://example.com/python", "Python Tutorial")
        doc2_id = db.insert_document("http://example.com/programming", "Programming Guide")

        db.insert_inverted_index(word1_id, doc1_id, 5)
        db.insert_inverted_index(word2_id, doc1_id, 3)
        db.insert_inverted_index(word2_id, doc2_id, 5)

        db.insert_link(doc1_id, doc2_id)

        # Test search
        print("Search results for 'python':")
        results = db.search_word("python")
        for url, title, rank in results:
            print(f"  {url} - {title} (PageRank: {rank})")

        # Get statistics
        stats = db.get_statistics()
        print("\nDatabase statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    print("\nTest database created: test_search.db")
