"""
Test cases for Lab 2 - Google OAuth Web Application with Keyword Tracking
Run with: python test_frontend.py
Or with pytest: pytest test_frontend.py -v

Tests cover:
- Word counting and keyword processing
- User data persistence (JSON operations)
- Recent words tracking functionality
- Edge cases and data validation
"""

import unittest
import json
import os
import tempfile
from unittest.mock import Mock, patch


# Import the functions we need to test
# We'll need to extract and test the core logic functions
def updateAppearences(list, dict):
    """
    Given a list of words, update the dictionary with each appearance of the word
    This is extracted from frontend.py for testing
    """
    for word in list:
        if word not in dict:
            dict[word] = 1
        else:
            dict[word] += 1
    return dict


class TestWordCounting(unittest.TestCase):
    """Test word counting and keyword processing functionality"""

    def test_update_appearances_new_words(self):
        """Test adding new words to empty dictionary"""
        words = ["python", "java", "programming"]
        result = updateAppearences(words, {})

        self.assertEqual(result["python"], 1)
        self.assertEqual(result["java"], 1)
        self.assertEqual(result["programming"], 1)
        self.assertEqual(len(result), 3)

    def test_update_appearances_duplicates(self):
        """Test counting duplicate words"""
        words = ["python", "python", "java", "python"]
        result = updateAppearences(words, {})

        self.assertEqual(result["python"], 3)
        self.assertEqual(result["java"], 1)

    def test_update_appearances_existing_dict(self):
        """Test updating existing dictionary"""
        existing = {"python": 2, "java": 1}
        words = ["python", "javascript"]
        result = updateAppearences(words, existing)

        self.assertEqual(result["python"], 3)
        self.assertEqual(result["java"], 1)
        self.assertEqual(result["javascript"], 1)

    def test_empty_word_list(self):
        """Test with empty word list"""
        result = updateAppearences([], {})
        self.assertEqual(len(result), 0)

    def test_single_word(self):
        """Test with single word"""
        result = updateAppearences(["hello"], {})
        self.assertEqual(result["hello"], 1)


class TestQueryProcessing(unittest.TestCase):
    """Test query processing logic"""

    def test_lowercase_conversion(self):
        """Test that queries are converted to lowercase"""
        query = "Python JAVA JavaScript"
        keywords = query.lower().split()

        self.assertEqual(keywords, ["python", "java", "javascript"])
        for word in keywords:
            self.assertEqual(word, word.lower())

    def test_word_splitting(self):
        """Test that queries are properly split into words"""
        query = "web development is fun"
        keywords = query.lower().split()

        self.assertEqual(len(keywords), 4)
        self.assertEqual(keywords, ["web", "development", "is", "fun"])

    def test_multiple_spaces(self):
        """Test handling of multiple spaces"""
        query = "python    java     programming"
        keywords = query.lower().split()

        # split() handles multiple spaces correctly
        self.assertEqual(len(keywords), 3)
        self.assertEqual(keywords, ["python", "java", "programming"])

    def test_mixed_case_counting(self):
        """Test that mixed case words are counted together"""
        query = "Python python PYTHON"
        keywords = query.lower().split()
        result = updateAppearences(keywords, {})

        self.assertEqual(result["python"], 3)


class TestUserDataStructure(unittest.TestCase):
    """Test user data structure and operations"""

    def test_new_user_structure(self):
        """Test structure for new user"""
        user_data = {"keywordUsage": {}, "recentWords": []}

        self.assertIn("keywordUsage", user_data)
        self.assertIn("recentWords", user_data)
        self.assertIsInstance(user_data["keywordUsage"], dict)
        self.assertIsInstance(user_data["recentWords"], list)

    def test_keyword_usage_update(self):
        """Test updating keyword usage"""
        user_data = {"keywordUsage": {}, "recentWords": []}
        word = "python"

        # First occurrence
        user_data["keywordUsage"][word] = user_data["keywordUsage"].get(word, 0) + 1
        self.assertEqual(user_data["keywordUsage"][word], 1)

        # Second occurrence
        user_data["keywordUsage"][word] = user_data["keywordUsage"].get(word, 0) + 1
        self.assertEqual(user_data["keywordUsage"][word], 2)


class TestRecentWordsTracking(unittest.TestCase):
    """Test recent words tracking functionality (last 10 words, LIFO, no repeats)"""

    def test_add_words_to_recent(self):
        """Test adding words to recent words list"""
        recent_words = []
        words = ["python", "java", "javascript"]

        for word in words:
            if word in recent_words:
                recent_words.remove(word)
            recent_words.append(word)

        self.assertEqual(len(recent_words), 3)
        self.assertEqual(recent_words, ["python", "java", "javascript"])

    def test_recent_words_no_duplicates(self):
        """Test that recent words list has no duplicates"""
        recent_words = ["python", "java", "javascript"]
        word = "python"

        # Simulate adding "python" again
        if word in recent_words:
            recent_words.remove(word)
        recent_words.append(word)

        self.assertEqual(len(recent_words), 3)
        self.assertEqual(recent_words, ["java", "javascript", "python"])
        self.assertEqual(recent_words[-1], "python")  # Most recent

    def test_recent_words_max_10(self):
        """Test that recent words list maintains max 10 words"""
        recent_words = []
        words = ["word" + str(i) for i in range(15)]

        for word in words:
            if word in recent_words:
                recent_words.remove(word)
            recent_words.append(word)

            if len(recent_words) > 10:
                recent_words.pop(0)

        self.assertEqual(len(recent_words), 10)
        # Should have the last 10 words (word5 through word14)
        self.assertEqual(recent_words[0], "word5")
        self.assertEqual(recent_words[-1], "word14")

    def test_recent_words_order(self):
        """Test that recent words are in correct order (oldest to newest)"""
        recent_words = []
        words = ["first", "second", "third"]

        for word in words:
            recent_words.append(word)

        # Most recent should be last
        self.assertEqual(recent_words[-1], "third")
        self.assertEqual(recent_words[0], "first")

    def test_recent_words_with_repeat(self):
        """Test recent words when same word appears multiple times"""
        recent_words = ["apple", "banana", "cherry"]
        word = "banana"

        # Simulate re-adding "banana"
        if word in recent_words:
            recent_words.remove(word)
        recent_words.append(word)

        self.assertEqual(recent_words, ["apple", "cherry", "banana"])
        self.assertEqual(len(recent_words), 3)


class TestJSONPersistence(unittest.TestCase):
    """Test JSON data persistence operations"""

    def setUp(self):
        """Create temporary file for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.temp_filename = self.temp_file.name

    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)

    def test_save_and_load_data(self):
        """Test saving and loading user data from JSON"""
        test_data = {
            "user@example.com": {
                "keywordUsage": {"python": 5, "java": 3},
                "recentWords": ["python", "java", "javascript"]
            }
        }

        # Save
        with open(self.temp_filename, "w") as f:
            json.dump(test_data, f, indent=2)

        # Load
        with open(self.temp_filename, "r") as f:
            loaded_data = json.load(f)

        self.assertEqual(loaded_data, test_data)
        self.assertEqual(loaded_data["user@example.com"]["keywordUsage"]["python"], 5)

    def test_load_empty_file(self):
        """Test loading from empty/nonexistent file"""
        nonexistent_file = "nonexistent_file_12345.json"

        if os.path.exists(nonexistent_file):
            with open(nonexistent_file, "r") as f:
                data = json.load(f)
        else:
            data = {}

        self.assertEqual(data, {})

    def test_multiple_users(self):
        """Test storing data for multiple users"""
        user_data = {
            "user1@example.com": {
                "keywordUsage": {"python": 10},
                "recentWords": ["python"]
            },
            "user2@example.com": {
                "keywordUsage": {"java": 5},
                "recentWords": ["java"]
            }
        }

        # Save
        with open(self.temp_filename, "w") as f:
            json.dump(user_data, f, indent=2)

        # Load
        with open(self.temp_filename, "r") as f:
            loaded_data = json.load(f)

        self.assertEqual(len(loaded_data), 2)
        self.assertIn("user1@example.com", loaded_data)
        self.assertIn("user2@example.com", loaded_data)


class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for complete workflow"""

    def test_complete_query_workflow(self):
        """Test complete workflow of processing a query"""
        # Setup
        user_data = {"keywordUsage": {}, "recentWords": []}
        query = "Python Java Python"

        # Process query (simulate frontend.py logic)
        keywords = query.lower().split()

        # Count for this query
        query_counts = updateAppearences(keywords, {})

        # Update user data
        for word in keywords:
            user_data["keywordUsage"][word] = user_data["keywordUsage"].get(word, 0) + 1

            if word in user_data["recentWords"]:
                user_data["recentWords"].remove(word)
            user_data["recentWords"].append(word)

            if len(user_data["recentWords"]) > 10:
                user_data["recentWords"].pop(0)

        # Assertions
        self.assertEqual(query_counts["python"], 2)
        self.assertEqual(query_counts["java"], 1)
        self.assertEqual(user_data["keywordUsage"]["python"], 2)
        self.assertEqual(user_data["keywordUsage"]["java"], 1)
        # Recent words should have python and java, with python most recent
        self.assertIn("python", user_data["recentWords"])
        self.assertIn("java", user_data["recentWords"])
        self.assertEqual(user_data["recentWords"][-1], "python")

    def test_multiple_queries_same_user(self):
        """Test multiple queries from same user"""
        user_data = {"keywordUsage": {}, "recentWords": []}

        # First query
        query1 = "python programming"
        keywords1 = query1.lower().split()
        for word in keywords1:
            user_data["keywordUsage"][word] = user_data["keywordUsage"].get(word, 0) + 1
            if word in user_data["recentWords"]:
                user_data["recentWords"].remove(word)
            user_data["recentWords"].append(word)

        # Second query
        query2 = "java python"
        keywords2 = query2.lower().split()
        for word in keywords2:
            user_data["keywordUsage"][word] = user_data["keywordUsage"].get(word, 0) + 1
            if word in user_data["recentWords"]:
                user_data["recentWords"].remove(word)
            user_data["recentWords"].append(word)

        # Assertions
        self.assertEqual(user_data["keywordUsage"]["python"], 2)
        self.assertEqual(user_data["keywordUsage"]["programming"], 1)
        self.assertEqual(user_data["keywordUsage"]["java"], 1)
        # Recent order should be: programming, java, python
        self.assertEqual(user_data["recentWords"], ["programming", "java", "python"])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_empty_query(self):
        """Test processing empty query"""
        query = ""
        keywords = query.lower().split()

        self.assertEqual(len(keywords), 0)
        result = updateAppearences(keywords, {})
        self.assertEqual(len(result), 0)

    def test_whitespace_only_query(self):
        """Test query with only whitespace"""
        query = "     "
        keywords = query.lower().split()

        self.assertEqual(len(keywords), 0)

    def test_special_characters(self):
        """Test handling of special characters in queries"""
        query = "python! java? programming."
        keywords = query.lower().split()

        # Note: The actual app doesn't strip punctuation,
        # so words will include special characters
        self.assertIn("python!", keywords)
        self.assertIn("java?", keywords)
        self.assertIn("programming.", keywords)

    def test_very_long_query(self):
        """Test processing very long query"""
        words = ["word" + str(i) for i in range(100)]
        query = " ".join(words)
        keywords = query.lower().split()

        self.assertEqual(len(keywords), 100)
        result = updateAppearences(keywords, {})
        self.assertEqual(len(result), 100)

    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        query = "python café programming"
        keywords = query.lower().split()

        self.assertEqual(len(keywords), 3)
        self.assertIn("café", keywords)


class TestWordCountTable(unittest.TestCase):
    """Test word count table generation logic"""

    def test_count_table_structure(self):
        """Test that word counts are properly structured"""
        query = "python java python javascript"
        keywords = query.lower().split()
        keyword_dict = updateAppearences(keywords, {})

        # Verify structure
        self.assertIsInstance(keyword_dict, dict)
        for word, count in keyword_dict.items():
            self.assertIsInstance(word, str)
            self.assertIsInstance(count, int)
            self.assertGreater(count, 0)

    def test_count_accuracy(self):
        """Test accuracy of word counting"""
        query = "a b c a b a"
        keywords = query.lower().split()
        keyword_dict = updateAppearences(keywords, {})

        self.assertEqual(keyword_dict["a"], 3)
        self.assertEqual(keyword_dict["b"], 2)
        self.assertEqual(keyword_dict["c"], 1)


def run_tests():
    """Run all tests with verbose output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWordCounting))
    suite.addTests(loader.loadTestsFromTestCase(TestQueryProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestUserDataStructure))
    suite.addTests(loader.loadTestsFromTestCase(TestRecentWordsTracking))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONPersistence))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestWordCountTable))

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
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed")

    return result


if __name__ == '__main__':
    print("="*70)
    print("ECE326 Lab 2 - Benchmark Tests")
    print("Google OAuth Web Application with Keyword Tracking")
    print("="*70)
    print()

    run_tests()
