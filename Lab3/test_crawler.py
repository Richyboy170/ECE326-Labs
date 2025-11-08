"""
Unit Tests for Lab 3 Crawler and Storage

This module contains unit tests for:
- PageRank algorithm
- Database storage operations
- Crawler functionality
"""

import unittest
import os
import sqlite3
from storage import SearchEngineDB
from pagerank import page_rank, normalize_page_rank


class TestPageRank(unittest.TestCase):
    """Test cases for PageRank algorithm"""

    def test_simple_graph(self):
        """Test PageRank with a simple 3-node graph"""
        links = {
            1: [2, 3],
            2: [3],
            3: [1]
        }
        scores = page_rank(links, num_iterations=20)

        # All pages should have positive scores
        self.assertGreater(scores[1], 0)
        self.assertGreater(scores[2], 0)
        self.assertGreater(scores[3], 0)

        # Page 3 should have the highest score (receives links from 1 and 2)
        self.assertGreater(scores[3], scores[1])
        self.assertGreater(scores[3], scores[2])

    def test_linear_graph(self):
        """Test PageRank with a linear chain"""
        links = {
            1: [2],
            2: [3],
            3: [4]
        }
        scores = page_rank(links, num_iterations=20)

        # All pages should have scores
        self.assertEqual(len(scores), 4)
        for page_id, score in scores.items():
            self.assertGreater(score, 0)

    def test_isolated_page(self):
        """Test PageRank with an isolated page (no outgoing links)"""
        links = {
            1: [2],
            2: []
        }
        scores = page_rank(links, num_iterations=20)
        self.assertGreater(scores[1], 0)
        self.assertGreater(scores[2], 0)

    def test_normalize(self):
        """Test PageRank normalization"""
        scores = {1: 10.0, 2: 20.0, 3: 30.0}
        normalized = normalize_page_rank(scores)

        # Sum should be 1.0
        total = sum(normalized.values())
        self.assertAlmostEqual(total, 1.0, places=5)

        # Relative ordering should be preserved
        self.assertGreater(normalized[3], normalized[2])
        self.assertGreater(normalized[2], normalized[1])


class TestSearchEngineDB(unittest.TestCase):
    """Test cases for database storage"""

    def setUp(self):
        """Set up test database"""
        self.test_db = 'test_search.db'
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = SearchEngineDB(self.test_db)

    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_insert_word(self):
        """Test inserting words into lexicon"""
        word_id1 = self.db.insert_word("python")
        word_id2 = self.db.insert_word("programming")
        word_id3 = self.db.insert_word("python")  # Duplicate

        self.assertIsInstance(word_id1, int)
        self.assertIsInstance(word_id2, int)
        self.assertEqual(word_id1, word_id3)  # Duplicate should return same ID
        self.assertNotEqual(word_id1, word_id2)

    def test_insert_document(self):
        """Test inserting documents"""
        doc_id1 = self.db.insert_document("http://example.com/page1", "Page 1")
        doc_id2 = self.db.insert_document("http://example.com/page2", "Page 2")
        doc_id3 = self.db.insert_document("http://example.com/page1")  # Duplicate

        self.assertIsInstance(doc_id1, int)
        self.assertIsInstance(doc_id2, int)
        self.assertEqual(doc_id1, doc_id3)  # Duplicate should return same ID
        self.assertNotEqual(doc_id1, doc_id2)

    def test_update_document_title(self):
        """Test updating document title"""
        doc_id = self.db.insert_document("http://example.com", "Old Title")
        self.db.update_document_title(doc_id, "New Title")

        # Verify update
        docs = self.db.get_all_documents()
        for d_id, url, title, rank in docs:
            if d_id == doc_id:
                self.assertEqual(title, "New Title")
                break
        else:
            self.fail("Document not found")

    def test_inverted_index(self):
        """Test inverted index operations"""
        word_id = self.db.insert_word("test")
        doc_id = self.db.insert_document("http://example.com")

        self.db.insert_inverted_index(word_id, doc_id, 5)

        # Test search
        results = self.db.search_word("test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], "http://example.com")

    def test_link_graph(self):
        """Test link graph operations"""
        doc_id1 = self.db.insert_document("http://example.com/page1")
        doc_id2 = self.db.insert_document("http://example.com/page2")
        doc_id3 = self.db.insert_document("http://example.com/page3")

        self.db.insert_link(doc_id1, doc_id2)
        self.db.insert_link(doc_id1, doc_id3)
        self.db.insert_link(doc_id2, doc_id3)

        # Get link graph
        links = self.db.get_link_graph()

        self.assertIn(doc_id1, links)
        self.assertIn(doc_id2, links)
        self.assertEqual(len(links[doc_id1]), 2)
        self.assertIn(doc_id2, links[doc_id1])
        self.assertIn(doc_id3, links[doc_id1])

    def test_page_rank_update(self):
        """Test updating PageRank scores"""
        doc_id1 = self.db.insert_document("http://example.com/page1")
        doc_id2 = self.db.insert_document("http://example.com/page2")

        page_ranks = {
            doc_id1: 0.75,
            doc_id2: 0.25
        }

        self.db.update_page_ranks(page_ranks)

        # Verify updates
        docs = self.db.get_all_documents()
        for d_id, url, title, rank in docs:
            if d_id in page_ranks:
                self.assertAlmostEqual(rank, page_ranks[d_id], places=5)

    def test_search_with_pagerank(self):
        """Test search results ordered by PageRank"""
        # Create documents
        doc_id1 = self.db.insert_document("http://example.com/low", "Low Rank")
        doc_id2 = self.db.insert_document("http://example.com/high", "High Rank")

        # Insert same word in both documents
        word_id = self.db.insert_word("search")
        self.db.insert_inverted_index(word_id, doc_id1, 5)
        self.db.insert_inverted_index(word_id, doc_id2, 5)

        # Set different PageRank scores
        self.db.update_page_ranks({doc_id1: 0.2, doc_id2: 0.8})

        # Search should return results ordered by PageRank
        results = self.db.search_word("search")
        self.assertEqual(len(results), 2)
        # First result should have higher PageRank
        self.assertGreater(results[0][2], results[1][2])
        self.assertEqual(results[0][0], "http://example.com/high")

    def test_statistics(self):
        """Test database statistics"""
        # Add some data
        word_id1 = self.db.insert_word("word1")
        word_id2 = self.db.insert_word("word2")
        doc_id1 = self.db.insert_document("http://example.com/1")
        doc_id2 = self.db.insert_document("http://example.com/2")
        self.db.insert_inverted_index(word_id1, doc_id1, 5)
        self.db.insert_link(doc_id1, doc_id2)

        stats = self.db.get_statistics()

        self.assertEqual(stats['total_words'], 2)
        self.assertEqual(stats['total_documents'], 2)
        self.assertEqual(stats['total_index_entries'], 1)
        self.assertEqual(stats['total_links'], 1)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflow"""

    def setUp(self):
        """Set up test database"""
        self.test_db = 'test_integration.db'
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = SearchEngineDB(self.test_db)

    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_complete_workflow(self):
        """Test complete indexing and search workflow"""
        # Step 1: Index some documents
        doc1 = self.db.insert_document("http://test.com/python", "Python Tutorial")
        doc2 = self.db.insert_document("http://test.com/java", "Java Guide")
        doc3 = self.db.insert_document("http://test.com/programming", "Programming Basics")

        # Step 2: Add words to documents
        python_id = self.db.insert_word("python")
        java_id = self.db.insert_word("java")
        programming_id = self.db.insert_word("programming")

        self.db.insert_inverted_index(python_id, doc1, 7)
        self.db.insert_inverted_index(programming_id, doc1, 3)
        self.db.insert_inverted_index(java_id, doc2, 7)
        self.db.insert_inverted_index(programming_id, doc2, 3)
        self.db.insert_inverted_index(programming_id, doc3, 7)

        # Step 3: Add links
        self.db.insert_link(doc1, doc3)
        self.db.insert_link(doc2, doc3)

        # Step 4: Compute PageRank
        links = self.db.get_link_graph()
        page_ranks = page_rank(links)
        page_ranks = normalize_page_rank(page_ranks)
        self.db.update_page_ranks(page_ranks)

        # Step 5: Search and verify results
        python_results = self.db.search_word("python")
        self.assertEqual(len(python_results), 1)
        self.assertEqual(python_results[0][0], "http://test.com/python")

        programming_results = self.db.search_word("programming")
        self.assertEqual(len(programming_results), 3)

        # doc3 should have highest PageRank (receives 2 links)
        self.assertEqual(programming_results[0][0], "http://test.com/programming")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestPageRank))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchEngineDB))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 60)
    print("ECE326 Lab 3 - Unit Tests")
    print("=" * 60)
    print()

    success = run_tests()

    print()
    print("=" * 60)
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
    print("=" * 60)
