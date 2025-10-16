"""
Test cases for Web Crawler - Lab 1
Run with: python test_crawler.py
Or with pytest: pytest test_crawler.py -v
"""

import unittest
import os
import tempfile
from crawler import crawler


class TestCrawlerBasics(unittest.TestCase):
    """Test basic crawler initialization and setup"""
    
    def setUp(self):
        """Create a temporary URLs file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write('https://www.example.com\n')
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_crawler_initializes(self):
        """Test that crawler object can be created"""
        bot = crawler(None, self.temp_file.name)
        self.assertIsNotNone(bot)
    
    def test_url_queue_populated(self):
        """Test that URLs are loaded into the queue"""
        bot = crawler(None, self.temp_file.name)
        self.assertGreater(len(bot._url_queue), 0)
    
    def test_data_structures_exist(self):
        """Test that all required data structures are initialized"""
        bot = crawler(None, self.temp_file.name)
        self.assertIsNotNone(bot._doc_id_cache)
        self.assertIsNotNone(bot._word_id_cache)
        self.assertIsNotNone(bot._inverted_index) ####


class TestInvertedIndex(unittest.TestCase):
    """Test inverted index functionality"""
    
    def setUp(self):
        """Set up crawler with example.com"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write('https://www.example.com\n')
        self.temp_file.close()
        self.bot = crawler(None, self.temp_file.name)
        self.bot.crawl(depth=0, timeout=5)
    
    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_inverted_index_created(self):
        """Test that inverted index is populated after crawling"""
        inverted = self.bot.get_inverted_index()
        self.assertGreater(len(inverted), 0, "Inverted index should have entries") ####
    
    def test_inverted_index_structure(self):
        """Test that inverted index has correct structure"""
        inverted = self.bot.get_inverted_index()
        
        for word_id, doc_ids in inverted.items():
            # Keys should be strings
            self.assertIsInstance(word_id, str)
            # Values should be sets
            self.assertIsInstance(doc_ids, set)
            # Sets should contain integers (doc IDs)
            for doc_id in doc_ids:
                self.assertIsInstance(doc_id, int)
    
    def test_resolved_inverted_index_created(self):
        """Test that resolved inverted index works"""
        resolved = self.bot.get_resolved_inverted_index()
        self.assertGreater(len(resolved), 0, "Resolved index should have entries")
    
    def test_resolved_inverted_index_structure(self):
        """Test that resolved inverted index has words and URLs"""
        resolved = self.bot.get_resolved_inverted_index()
        
        for word, urls in resolved.items():
            # Keys should be strings (words)
            self.assertIsInstance(word, str)
            # Values should be sets of URLs
            self.assertIsInstance(urls, set)
            for url in urls:
                self.assertIsInstance(url, str)
                self.assertTrue(url.startswith('http'), f"URL should start with http: {url}")
    
    def test_word_appears_in_documents(self):
        """Test that common words appear in indexed documents"""
        resolved = self.bot.get_resolved_inverted_index()
        
        # example.com should have word "example"
        self.assertIn('example', resolved, "Word 'example' should be in index")
        self.assertGreater(len(resolved['example']), 0, "Word 'example' should have documents")


class TestDocumentIndexing(unittest.TestCase):
    """Test document and word ID assignment"""
    
    def setUp(self):
        """Create crawler with test URL"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write('https://www.example.com\n')
        self.temp_file.close()
        self.bot = crawler(None, self.temp_file.name)
        self.bot.crawl(depth=0, timeout=5)
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_documents_have_unique_ids(self):
        """Test that each document gets a unique ID"""
        doc_ids = list(self.bot._doc_id_cache.values())
        self.assertEqual(len(doc_ids), len(set(doc_ids)), "Document IDs should be unique")
    
    def test_words_have_unique_ids(self):
        """Test that each word gets a unique ID"""
        word_ids = list(self.bot._word_id_cache.values())
        self.assertEqual(len(word_ids), len(set(word_ids)), "Word IDs should be unique")
    
    def test_document_id_cache_populated(self):
        """Test that document ID cache is populated"""
        self.assertGreater(len(self.bot._doc_id_cache), 0, "Should have cached document IDs")
    
    def test_word_id_cache_populated(self):
        """Test that word ID cache is populated"""
        self.assertGreater(len(self.bot._word_id_cache), 0, "Should have cached word IDs")


class TestWordParsing(unittest.TestCase):
    """Test word parsing and filtering"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write('https://www.example.com\n')
        self.temp_file.close()
        self.bot = crawler(None, self.temp_file.name)
        self.bot.crawl(depth=0, timeout=5)
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_words_are_lowercase(self):
        """Test that all words are converted to lowercase"""
        for word in self.bot._word_id_cache.keys():
            self.assertEqual(word, word.lower(), f"Word '{word}' should be lowercase")
    
    def test_ignored_words_filtered(self):
        """Test that common words are filtered out"""
        # Words like 'the', 'a', 'is' should be ignored
        ignored_words = {'the', 'a', 'is', 'it', 'and', 'or'}
        indexed_words = set(self.bot._word_id_cache.keys())
        
        # Check that ignored words are not in the index
        for ignored in ignored_words:
            self.assertNotIn(ignored, indexed_words, 
                           f"Ignored word '{ignored}' should not be indexed")


class TestURLHandling(unittest.TestCase):
    """Test URL processing"""
    
    def test_multiple_urls(self):
        """Test crawling multiple URLs"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write('https://www.example.com\n')
        temp_file.write('https://www.wikipedia.org\n')
        temp_file.close()
        
        bot = crawler(None, temp_file.name)
        bot.crawl(depth=0, timeout=5)
        
        # Should have processed at least one URL
        self.assertGreater(len(bot._doc_id_cache), 0)
        
        os.remove(temp_file.name)
    
    def test_duplicate_urls_not_reindexed(self):
        """Test that duplicate URLs are not crawled twice"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write('https://www.example.com\n')
        temp_file.write('https://www.example.com\n')  # Duplicate
        temp_file.close()
        
        bot = crawler(None, temp_file.name)
        bot.crawl(depth=0, timeout=5)
        
        # Should only have one entry for example.com
        example_count = sum(1 for url in bot._doc_id_cache.keys() 
                          if 'example.com' in url)
        self.assertEqual(example_count, 1, "Duplicate URL should only be indexed once")
        
        os.remove(temp_file.name)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_empty_urls_file(self):
        """Test handling of empty URLs file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.close()  # Empty file
        
        bot = crawler(None, temp_file.name)
        self.assertEqual(len(bot._url_queue), 0, "URL queue should be empty")
        
        bot.crawl(depth=0, timeout=5)
        inverted = bot.get_inverted_index()
        self.assertEqual(len(inverted), 0, "Should have no words indexed")
        
        os.remove(temp_file.name)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent URLs file"""
        bot = crawler(None, "nonexistent_file_12345.txt")
        self.assertEqual(len(bot._url_queue), 0, "URL queue should be empty for missing file")
    
    def test_invalid_url(self):
        """Test handling of invalid URL (should not crash)"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.write('http://this-domain-definitely-does-not-exist-12345.com\n')
        temp_file.close()
        
        bot = crawler(None, temp_file.name)
        # Should not crash
        bot.crawl(depth=0, timeout=2)
        
        os.remove(temp_file.name)


class TestConsistency(unittest.TestCase):
    """Test consistency between data structures"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        self.temp_file.write('https://www.example.com\n')
        self.temp_file.close()
        self.bot = crawler(None, self.temp_file.name)
        self.bot.crawl(depth=0, timeout=5)
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
    def test_inverted_index_word_ids_in_lexicon(self):
        """Test that all word IDs in inverted index exist in word cache"""
        inverted = self.bot.get_inverted_index()
        word_ids_in_cache = set(self.bot._word_id_cache.values())
        
        for word_id_str in inverted.keys():
            word_id = int(word_id_str)
            self.assertIn(word_id, word_ids_in_cache, 
                         f"Word ID {word_id} in inverted index but not in cache")
    
    def test_inverted_index_doc_ids_in_cache(self):
        """Test that all doc IDs in inverted index exist in doc cache"""
        inverted = self.bot.get_inverted_index()
        doc_ids_in_cache = set(self.bot._doc_id_cache.values())
        
        for doc_ids in inverted.values():
            for doc_id in doc_ids:
                self.assertIn(doc_id, doc_ids_in_cache,
                            f"Doc ID {doc_id} in inverted index but not in cache")
    
    def test_resolved_index_consistency(self):
        """Test that resolved index matches raw inverted index"""
        inverted = self.bot.get_inverted_index()
        resolved = self.bot.get_resolved_inverted_index()
        
        # Number of words should match (or be less if some words can't be resolved)
        self.assertLessEqual(len(resolved), len(inverted),
                            "Resolved index should have same or fewer entries")


def run_tests():
    """Run all tests with verbose output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCrawlerBasics))
    suite.addTests(loader.loadTestsFromTestCase(TestInvertedIndex))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentIndexing))
    suite.addTests(loader.loadTestsFromTestCase(TestWordParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestURLHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestConsistency))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
    
    return result


if __name__ == '__main__':
    run_tests()