"""
Query Analytics and Statistics Tracking

This module tracks and analyzes search query patterns including:
- Popular search queries
- Search frequency over time
- Click-through rates (CTR)
- Query response times
- User search patterns

This data helps improve search quality and understand user behavior.
"""

import sqlite3
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import json


class SearchAnalytics:
    """
    Analytics system for tracking search engine usage and performance
    """

    def __init__(self, db_file: str = 'analytics.db'):
        """
        Initialize analytics database

        Args:
            db_file: Path to analytics database file
        """
        self.db_file = db_file
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Create analytics tables"""

        # Query Log: tracks every search query
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS QueryLog (
                query_id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                timestamp REAL NOT NULL,
                num_results INTEGER DEFAULT 0,
                response_time_ms REAL,
                user_ip TEXT,
                user_agent TEXT
            )
        ''')

        # Click Log: tracks which results users clicked
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ClickLog (
                click_id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_id INTEGER,
                url TEXT NOT NULL,
                position INTEGER,
                timestamp REAL NOT NULL,
                FOREIGN KEY (query_id) REFERENCES QueryLog(query_id)
            )
        ''')

        # Popular Queries: materialized view updated periodically
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS PopularQueries (
                query TEXT PRIMARY KEY,
                count INTEGER DEFAULT 0,
                last_searched REAL,
                avg_ctr REAL DEFAULT 0.0
            )
        ''')

        # Performance Metrics
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS PerformanceMetrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp REAL NOT NULL
            )
        ''')

        # Create indexes
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_query_timestamp ON QueryLog(timestamp)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_query_text ON QueryLog(query)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_click_query ON ClickLog(query_id)
        ''')

        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_popular_count ON PopularQueries(count DESC)
        ''')

        self.conn.commit()

    def log_query(self, query: str, num_results: int, response_time_ms: float,
                  user_ip: str = None, user_agent: str = None) -> int:
        """
        Log a search query

        Args:
            query: Search query text
            num_results: Number of results returned
            response_time_ms: Query response time in milliseconds
            user_ip: User IP address (optional)
            user_agent: User agent string (optional)

        Returns:
            query_id for this logged query
        """
        timestamp = time.time()

        self.cursor.execute('''
            INSERT INTO QueryLog (query, timestamp, num_results, response_time_ms, user_ip, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (query, timestamp, num_results, response_time_ms, user_ip, user_agent))

        self.conn.commit()

        query_id = self.cursor.lastrowid

        # Update popular queries
        self._update_popular_query(query, timestamp)

        return query_id

    def log_click(self, query_id: int, url: str, position: int):
        """
        Log a click on a search result

        Args:
            query_id: ID of the query from log_query
            url: URL that was clicked
            position: Position of result in search results (1-indexed)
        """
        timestamp = time.time()

        self.cursor.execute('''
            INSERT INTO ClickLog (query_id, url, position, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (query_id, url, position, timestamp))

        self.conn.commit()

        # Update CTR for this query
        self._update_query_ctr(query_id)

    def _update_popular_query(self, query: str, timestamp: float):
        """Update popular queries table"""
        normalized_query = query.lower().strip()

        self.cursor.execute('''
            INSERT INTO PopularQueries (query, count, last_searched)
            VALUES (?, 1, ?)
            ON CONFLICT(query) DO UPDATE SET
                count = count + 1,
                last_searched = ?
        ''', (normalized_query, timestamp, timestamp))

        self.conn.commit()

    def _update_query_ctr(self, query_id: int):
        """Update click-through rate for a query"""
        # Get the query text
        self.cursor.execute('SELECT query FROM QueryLog WHERE query_id = ?', (query_id,))
        result = self.cursor.fetchone()

        if not result:
            return

        query = result[0].lower().strip()

        # Calculate average CTR
        self.cursor.execute('''
            SELECT
                COUNT(DISTINCT ql.query_id) as total_queries,
                COUNT(DISTINCT cl.click_id) as total_clicks
            FROM QueryLog ql
            LEFT JOIN ClickLog cl ON ql.query_id = cl.query_id
            WHERE LOWER(ql.query) = ?
        ''', (query,))

        total_queries, total_clicks = self.cursor.fetchone()

        if total_queries > 0:
            avg_ctr = (total_clicks or 0) / total_queries

            self.cursor.execute('''
                UPDATE PopularQueries
                SET avg_ctr = ?
                WHERE query = ?
            ''', (avg_ctr, query))

            self.conn.commit()

    def get_popular_queries(self, limit: int = 10, min_count: int = 1) -> List[Tuple[str, int, float]]:
        """
        Get most popular search queries

        Args:
            limit: Maximum number of queries to return
            min_count: Minimum search count to include

        Returns:
            List of tuples: (query, count, avg_ctr)
        """
        self.cursor.execute('''
            SELECT query, count, avg_ctr
            FROM PopularQueries
            WHERE count >= ?
            ORDER BY count DESC
            LIMIT ?
        ''', (min_count, limit))

        return self.cursor.fetchall()

    def get_recent_queries(self, hours: int = 24, limit: int = 100) -> List[Tuple[str, str, int]]:
        """
        Get recent search queries

        Args:
            hours: Number of hours to look back
            limit: Maximum number of queries to return

        Returns:
            List of tuples: (query, timestamp, num_results)
        """
        cutoff_time = time.time() - (hours * 3600)

        self.cursor.execute('''
            SELECT query, timestamp, num_results
            FROM QueryLog
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (cutoff_time, limit))

        results = []
        for query, timestamp, num_results in self.cursor.fetchall():
            dt = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            results.append((query, dt, num_results))

        return results

    def get_query_stats(self, query: str) -> Dict[str, any]:
        """
        Get detailed statistics for a specific query

        Args:
            query: Query to analyze

        Returns:
            Dictionary with query statistics
        """
        normalized_query = query.lower().strip()

        # Get total searches
        self.cursor.execute('''
            SELECT COUNT(*) FROM QueryLog WHERE LOWER(query) = ?
        ''', (normalized_query,))
        total_searches = self.cursor.fetchone()[0]

        # Get total clicks
        self.cursor.execute('''
            SELECT COUNT(*)
            FROM ClickLog cl
            JOIN QueryLog ql ON cl.query_id = ql.query_id
            WHERE LOWER(ql.query) = ?
        ''', (normalized_query,))
        total_clicks = self.cursor.fetchone()[0]

        # Get average response time
        self.cursor.execute('''
            SELECT AVG(response_time_ms)
            FROM QueryLog
            WHERE LOWER(query) = ?
        ''', (normalized_query,))
        avg_response_time = self.cursor.fetchone()[0] or 0

        # Get average number of results
        self.cursor.execute('''
            SELECT AVG(num_results)
            FROM QueryLog
            WHERE LOWER(query) = ?
        ''', (normalized_query,))
        avg_num_results = self.cursor.fetchone()[0] or 0

        # Get most clicked URLs
        self.cursor.execute('''
            SELECT cl.url, COUNT(*) as click_count
            FROM ClickLog cl
            JOIN QueryLog ql ON cl.query_id = ql.query_id
            WHERE LOWER(ql.query) = ?
            GROUP BY cl.url
            ORDER BY click_count DESC
            LIMIT 5
        ''', (normalized_query,))
        top_clicks = self.cursor.fetchall()

        ctr = (total_clicks / total_searches * 100) if total_searches > 0 else 0

        return {
            'query': query,
            'total_searches': total_searches,
            'total_clicks': total_clicks,
            'ctr': ctr,
            'avg_response_time_ms': avg_response_time,
            'avg_num_results': avg_num_results,
            'top_clicked_urls': top_clicks
        }

    def get_performance_summary(self, hours: int = 24) -> Dict[str, any]:
        """
        Get overall performance summary

        Args:
            hours: Number of hours to analyze

        Returns:
            Dictionary with performance metrics
        """
        cutoff_time = time.time() - (hours * 3600)

        # Total queries
        self.cursor.execute('''
            SELECT COUNT(*) FROM QueryLog WHERE timestamp >= ?
        ''', (cutoff_time,))
        total_queries = self.cursor.fetchone()[0]

        # Average response time
        self.cursor.execute('''
            SELECT AVG(response_time_ms) FROM QueryLog WHERE timestamp >= ?
        ''', (cutoff_time,))
        avg_response_time = self.cursor.fetchone()[0] or 0

        # Queries with zero results
        self.cursor.execute('''
            SELECT COUNT(*) FROM QueryLog
            WHERE timestamp >= ? AND num_results = 0
        ''', (cutoff_time,))
        zero_result_queries = self.cursor.fetchone()[0]

        # Total clicks
        self.cursor.execute('''
            SELECT COUNT(*)
            FROM ClickLog
            WHERE timestamp >= ?
        ''', (cutoff_time,))
        total_clicks = self.cursor.fetchone()[0]

        overall_ctr = (total_clicks / total_queries * 100) if total_queries > 0 else 0
        zero_result_rate = (zero_result_queries / total_queries * 100) if total_queries > 0 else 0

        return {
            'time_period_hours': hours,
            'total_queries': total_queries,
            'total_clicks': total_clicks,
            'overall_ctr': overall_ctr,
            'avg_response_time_ms': avg_response_time,
            'zero_result_queries': zero_result_queries,
            'zero_result_rate': zero_result_rate
        }

    def log_performance_metric(self, metric_name: str, metric_value: float):
        """
        Log a custom performance metric

        Args:
            metric_name: Name of the metric
            metric_value: Value of the metric
        """
        timestamp = time.time()

        self.cursor.execute('''
            INSERT INTO PerformanceMetrics (metric_name, metric_value, timestamp)
            VALUES (?, ?, ?)
        ''', (metric_name, metric_value, timestamp))

        self.conn.commit()

    def close(self):
        """Close database connection"""
        self.conn.commit()
        self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Global analytics instance
_analytics = None


def get_analytics(db_file: str = 'analytics.db') -> SearchAnalytics:
    """
    Get or create global analytics instance

    Args:
        db_file: Database file path

    Returns:
        SearchAnalytics instance
    """
    global _analytics
    if _analytics is None:
        _analytics = SearchAnalytics(db_file)
    return _analytics


if __name__ == "__main__":
    # Test analytics system
    print("Testing Search Analytics System\n")

    with SearchAnalytics('test_analytics.db') as analytics:
        # Log some queries
        print("Logging sample queries...")
        q1 = analytics.log_query('python tutorial', 50, 125.5)
        q2 = analytics.log_query('python tutorial', 50, 98.2)
        q3 = analytics.log_query('java programming', 30, 150.0)
        q4 = analytics.log_query('machine learning', 100, 200.5)

        # Log some clicks
        print("Logging clicks...")
        analytics.log_click(q1, 'http://example.com/python', 1)
        analytics.log_click(q2, 'http://example.com/python', 1)
        analytics.log_click(q3, 'http://example.com/java', 2)

        # Get popular queries
        print("\nPopular Queries:")
        for query, count, ctr in analytics.get_popular_queries(limit=5):
            print(f"  '{query}': {count} searches, {ctr*100:.1f}% CTR")

        # Get query stats
        print("\nStats for 'python tutorial':")
        stats = analytics.get_query_stats('python tutorial')
        for key, value in stats.items():
            print(f"  {key}: {value}")

        # Get performance summary
        print("\nPerformance Summary (24h):")
        perf = analytics.get_performance_summary(hours=24)
        for key, value in perf.items():
            print(f"  {key}: {value}")

    print("\nTest analytics database created: test_analytics.db")
