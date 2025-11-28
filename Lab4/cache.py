"""
Query Result Caching System

This module implements an LRU (Least Recently Used) cache for search query results.
Caching significantly improves performance for repeated queries.

Features:
- LRU eviction policy
- Configurable cache size
- Cache hit/miss statistics
- TTL (Time To Live) support for cache entries
"""

import time
from collections import OrderedDict
from typing import Any, Optional, Dict
import threading


class LRUCache:
    """
    Thread-safe LRU Cache implementation with TTL support
    """

    def __init__(self, capacity: int = 1000, ttl: int = 3600):
        """
        Initialize LRU cache

        Args:
            capacity: Maximum number of items to cache
            ttl: Time to live for cache entries in seconds (default: 1 hour)
        """
        self.capacity = capacity
        self.ttl = ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.Lock()

        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            # Check if entry has expired
            if time.time() - self.timestamps[key] > self.ttl:
                # Entry expired, remove it
                del self.cache[key]
                del self.timestamps[key]
                self.misses += 1
                return None

            # Move to end (mark as recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        """
        Put value in cache

        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            if key in self.cache:
                # Update existing entry
                self.cache.move_to_end(key)
            else:
                # Add new entry
                if len(self.cache) >= self.capacity:
                    # Evict least recently used item
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    del self.timestamps[oldest_key]
                    self.evictions += 1

            self.cache[key] = value
            self.timestamps[key] = time.time()

    def clear(self) -> None:
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0

            return {
                'capacity': self.capacity,
                'size': len(self.cache),
                'hits': self.hits,
                'misses': self.misses,
                'evictions': self.evictions,
                'hit_rate': hit_rate,
                'total_requests': total_requests
            }

    def reset_stats(self) -> None:
        """Reset statistics counters"""
        with self.lock:
            self.hits = 0
            self.misses = 0
            self.evictions = 0


class QueryCache:
    """
    High-level cache specifically for search queries
    """

    def __init__(self, capacity: int = 500, ttl: int = 1800):
        """
        Initialize query cache

        Args:
            capacity: Maximum number of queries to cache
            ttl: Time to live in seconds (default: 30 minutes)
        """
        self.cache = LRUCache(capacity=capacity, ttl=ttl)

    def _make_key(self, query: str, page: int = 1, per_page: int = 5) -> str:
        """
        Create cache key from query parameters

        Args:
            query: Search query
            page: Page number
            per_page: Results per page

        Returns:
            Cache key string
        """
        # Normalize query (lowercase, strip whitespace)
        normalized_query = query.lower().strip()
        return f"{normalized_query}:{page}:{per_page}"

    def get_results(self, query: str, page: int = 1, per_page: int = 5) -> Optional[Any]:
        """
        Get cached search results

        Args:
            query: Search query
            page: Page number
            per_page: Results per page

        Returns:
            Cached results if available, None otherwise
        """
        key = self._make_key(query, page, per_page)
        return self.cache.get(key)

    def cache_results(self, query: str, results: Any, page: int = 1, per_page: int = 5) -> None:
        """
        Cache search results

        Args:
            query: Search query
            results: Search results to cache
            page: Page number
            per_page: Results per page
        """
        key = self._make_key(query, page, per_page)
        self.cache.put(key, results)

    def invalidate(self, query: Optional[str] = None) -> None:
        """
        Invalidate cache entries

        Args:
            query: If provided, invalidate only this query. Otherwise clear all.
        """
        if query is None:
            self.cache.clear()
        else:
            # Remove all pages for this query
            normalized_query = query.lower().strip()
            with self.cache.lock:
                keys_to_remove = [
                    k for k in self.cache.cache.keys()
                    if k.startswith(normalized_query + ":")
                ]
                for key in keys_to_remove:
                    del self.cache.cache[key]
                    if key in self.cache.timestamps:
                        del self.cache.timestamps[key]

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()

    def reset_stats(self) -> None:
        """Reset statistics"""
        self.cache.reset_stats()


# Global query cache instance
_query_cache = None


def get_query_cache(capacity: int = 500, ttl: int = 1800) -> QueryCache:
    """
    Get or create global query cache instance

    Args:
        capacity: Cache capacity (only used on first call)
        ttl: Time to live in seconds (only used on first call)

    Returns:
        QueryCache instance
    """
    global _query_cache
    if _query_cache is None:
        _query_cache = QueryCache(capacity=capacity, ttl=ttl)
    return _query_cache


if __name__ == "__main__":
    # Test the caching system
    print("Testing Query Cache System\n")

    cache = QueryCache(capacity=3, ttl=5)

    # Cache some results
    print("Caching results for 'python'...")
    cache.cache_results('python', [('url1', 'Python Tutorial', 0.9)], page=1)

    print("Caching results for 'java'...")
    cache.cache_results('java', [('url2', 'Java Guide', 0.8)], page=1)

    # Test cache hit
    print("\nRetrieving cached 'python':")
    result = cache.get_results('python', page=1)
    print(f"  Result: {result}")

    # Test cache miss
    print("\nRetrieving uncached 'c++':")
    result = cache.get_results('c++', page=1)
    print(f"  Result: {result}")

    # Test LRU eviction
    print("\nCaching results for 'javascript', 'go'...")
    cache.cache_results('javascript', [('url3', 'JS Guide', 0.7)], page=1)
    cache.cache_results('go', [('url4', 'Go Tutorial', 0.85)], page=1)

    # Check stats
    print("\nCache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test TTL
    print("\nWaiting 6 seconds for TTL expiration...")
    time.sleep(6)

    print("Trying to retrieve 'go' after TTL:")
    result = cache.get_results('go', page=1)
    print(f"  Result: {result}")

    print("\nFinal Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
