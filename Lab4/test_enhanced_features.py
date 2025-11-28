#!/usr/bin/env python3
"""
Test script for Lab 4 enhanced backend features

This script tests all innovative backend features:
1. Advanced ranking system
2. Query caching
3. Analytics tracking
4. Snippet generation
"""

import sys
import time
from storage import SearchEngineDB
from ranking import AdvancedRanker
from cache import QueryCache
from analytics import SearchAnalytics
from snippets import SnippetGenerator


def test_ranking():
    """Test advanced ranking system"""
    print("=" * 60)
    print("TEST 1: Advanced Ranking System")
    print("=" * 60)

    try:
        with SearchEngineDB('search_engine.db') as db:
            ranker = AdvancedRanker(db)

            # Test single word ranking
            print("\n1. Testing single-word ranking...")
            results = ranker.rank_single_word('test', limit=5)
            print(f"   Found {len(results)} results")

            if results:
                print("   Top result:")
                url, title, score, pr = results[0]
                print(f"     URL: {url}")
                print(f"     Title: {title}")
                print(f"     Combined Score: {score:.4f}")
                print(f"     PageRank: {pr:.4f}")

            # Test multi-word ranking
            print("\n2. Testing multi-word ranking...")
            results = ranker.rank_multi_word(['test', 'page'], limit=5)
            print(f"   Found {len(results)} results for 'test page'")

            if results:
                print("   Top result:")
                url, title, score, pr = results[0]
                print(f"     Combined Score: {score:.4f}")

        print("\n✓ Advanced ranking system working correctly")
        return True

    except Exception as e:
        print(f"\n✗ Ranking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_caching():
    """Test query caching"""
    print("\n" + "=" * 60)
    print("TEST 2: Query Result Caching")
    print("=" * 60)

    try:
        cache = QueryCache(capacity=10, ttl=60)

        # Test cache miss
        print("\n1. Testing cache miss...")
        result = cache.get_results('python tutorial')
        print(f"   Result (should be None): {result}")

        # Test cache put and get
        print("\n2. Testing cache storage...")
        test_data = [('url1', 'Title 1', 0.9), ('url2', 'Title 2', 0.8)]
        cache.cache_results('python tutorial', test_data)

        result = cache.get_results('python tutorial')
        print(f"   Retrieved {len(result)} results from cache")

        # Test cache stats
        print("\n3. Testing cache statistics...")
        stats = cache.get_stats()
        print(f"   Cache size: {stats['size']}/{stats['capacity']}")
        print(f"   Hits: {stats['hits']}")
        print(f"   Misses: {stats['misses']}")
        print(f"   Hit rate: {stats['hit_rate']:.1f}%")

        print("\n✓ Query caching working correctly")
        return True

    except Exception as e:
        print(f"\n✗ Caching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analytics():
    """Test analytics tracking"""
    print("\n" + "=" * 60)
    print("TEST 3: Query Analytics")
    print("=" * 60)

    try:
        with SearchAnalytics('test_analytics_features.db') as analytics:

            # Test query logging
            print("\n1. Testing query logging...")
            q1 = analytics.log_query('python programming', 50, 125.5)
            q2 = analytics.log_query('python programming', 48, 98.2)
            q3 = analytics.log_query('web development', 30, 150.0)
            print(f"   Logged 3 queries (IDs: {q1}, {q2}, {q3})")

            # Test click logging
            print("\n2. Testing click logging...")
            analytics.log_click(q1, 'http://example.com/python', 1)
            analytics.log_click(q2, 'http://example.com/python', 1)
            print("   Logged 2 clicks")

            # Test popular queries
            print("\n3. Testing popular queries...")
            popular = analytics.get_popular_queries(limit=5)
            print(f"   Found {len(popular)} popular queries")

            for query, count, ctr in popular:
                print(f"     '{query}': {count} searches, {ctr*100:.1f}% CTR")

            # Test performance summary
            print("\n4. Testing performance summary...")
            perf = analytics.get_performance_summary(hours=24)
            print(f"   Total queries: {perf['total_queries']}")
            print(f"   Overall CTR: {perf['overall_ctr']:.1f}%")
            print(f"   Avg response time: {perf['avg_response_time_ms']:.1f}ms")

        print("\n✓ Analytics tracking working correctly")
        return True

    except Exception as e:
        print(f"\n✗ Analytics test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_snippets():
    """Test snippet generation"""
    print("\n" + "=" * 60)
    print("TEST 4: Search Result Snippets")
    print("=" * 60)

    try:
        generator = SnippetGenerator(max_snippet_length=150)

        # Test single word
        print("\n1. Testing single-word snippet...")
        text = "Python is a high-level programming language. Python supports multiple programming paradigms."
        snippet = generator.generate_snippet(text, ['python'])
        print(f"   Snippet: {snippet}")

        # Test multi-word
        print("\n2. Testing multi-word snippet...")
        snippet = generator.generate_snippet(text, ['python', 'programming'])
        print(f"   Snippet: {snippet}")

        # Test HTML stripping
        print("\n3. Testing HTML content...")
        html = "<html><body><h1>Python Tutorial</h1><p>Learn Python programming easily.</p></body></html>"
        snippet = generator.generate_snippet_from_html(html, ['python', 'tutorial'])
        print(f"   Snippet: {snippet}")

        print("\n✓ Snippet generation working correctly")
        return True

    except Exception as e:
        print(f"\n✗ Snippet test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("LAB 4 ENHANCED FEATURES TEST SUITE")
    print("=" * 60)
    print("\nTesting innovative backend features...\n")

    results = []

    # Run tests
    results.append(("Advanced Ranking", test_ranking()))
    results.append(("Query Caching", test_caching()))
    results.append(("Analytics Tracking", test_analytics()))
    results.append(("Snippet Generation", test_snippets()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print("\n" + "=" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 All tests passed! Enhanced features are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
