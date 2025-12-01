import json
import os
import time
from dotenv import load_dotenv
from beaker.middleware import SessionMiddleware
import bottle
from bottle import run, get, post, request, response, route, error, template, static_file, Bottle

# Import our backend modules
from storage import SearchEngineDB
from ranking import AdvancedRanker
from cache import get_query_cache
from analytics import get_analytics
from snippets import get_snippet_generator

# Database connections
DB_FILE = "search_engine.db"
ANALYTICS_DB_FILE = "analytics.db"
RESULTS_PER_PAGE = 5
def get_db():
    """Get database connection"""
    return SearchEngineDB(DB_FILE)

PORT = 8080

# Initialize global instances
query_cache = get_query_cache(capacity=500, ttl=1800)  # Cache 500 queries for 30 mins
analytics = get_analytics(ANALYTICS_DB_FILE)
snippet_gen = get_snippet_generator()

# Create app
app = Bottle()

# Session settings
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': True,
    'session.data_dir': './sessions',
    'session.auto': True
}
appWithSessions = SessionMiddleware(app, session_opts)

# Query screen for homepage
@app.route('/')
def home():

    # Get database statistics
    try:
        with get_db() as db:
            stats = db.get_statistics()
            stats_html = f"""
            <div class="stats">
                <h3>Index Statistics</h3>
                <p>Total documents: {stats['total_documents']}</p>
                <p>Total words: {stats['total_words']}</p>
                <p>Total links: {stats['total_links']}</p>
            </div>
            """
    except Exception as e:
        stats_html = f'<div class="info"><p style="color: red;">Database not found. Please run the crawler first.</p></div>'

    return bottle.template('static/index_enhanced.tpl', STATS=stats_html)

# Result page for query
@app.route("/search")
def process_query():
    """
    Enhanced search with multi-word support, caching, analytics, and advanced ranking
    """

    # Start timing for analytics
    start_time = time.time()

    # Get query with multiple keywords
    query = request.query.keywords or ""
    query = query.strip()

    # Get the current page number (default is 1)
    page = int(request.query.page or 1)
    per_page = RESULTS_PER_PAGE

    # Check cache first
    cached_results = query_cache.get_results(query, page, per_page)

    # Cache hit - grab cached results
    if cached_results is not None:
        
        urls, total_pages, cache_hit = cached_results
        response_time_ms = (time.time() - start_time) * 1000

        # Log to analytics
        analytics.log_query(query, len(urls) * total_pages, response_time_ms, user_ip=request.remote_addr)

        return template('static/resultPage_enhanced.tpl',
                        urls=urls,
                        query=query,
                        page=page,
                        total_pages=total_pages,
                        cache_hit=True,
                        response_time=f"{response_time_ms:.2f}ms")

    # Cache miss - perform search
    try:
        with get_db() as db:
            # Use advanced ranking system
            ranker = AdvancedRanker(db)

            # Split query into words for multi-word search
            query_words = query.split()

            if not query_words:
                urls = []
            elif len(query_words) == 1:
                # Single word search
                urls = ranker.rank_single_word(query_words[0], limit=1000)
            else:
                # Multi-word search
                urls = ranker.rank_multi_word(query_words, limit=1000)

            # Generate snippets for results, we use the title as a simple snippet
            enhanced_urls = []

            for url, title, score, pagerank in urls:
                # Generate a simple snippet (in production, use actual page content)
                snippet = title or "No description available"

                # Highlight query words in snippet
                for word in query_words:
                    snippet = snippet.replace(word, f"<b>{word}</b>")
                    snippet = snippet.replace(word.capitalize(), f"<b>{word.capitalize()}</b>")

                enhanced_urls.append((url, title, score, pagerank, snippet))

    except Exception as e:
        return f"<body style=\"text-align: center;\"><h1>Error: {e}</h1><a href=\"/\">Return to EUREKA! Homepage</a></body>"

    # Calculate response time
    response_time_ms = (time.time() - start_time) * 1000

    # Log to analytics
    analytics.log_query(query, len(enhanced_urls), response_time_ms, user_ip=request.remote_addr)

    # Paginate results
    start = (page - 1) * per_page
    end = start + per_page
    page_urls = enhanced_urls[start:end]
    total_pages = (len(enhanced_urls) + per_page - 1) // per_page or 1

    # Cache the results
    query_cache.cache_results(query, (page_urls, total_pages, False), page, per_page)

    return template('static/resultPage_enhanced.tpl',
                    urls=page_urls,
                    query=query,
                    page=page,
                    total_pages=total_pages,
                    cache_hit=False,
                    response_time=f"{response_time_ms:.2f}ms")

# Analytics dashboard page
@app.route('/analytics')
def show_analytics():

    # Get popular queries
    popular = analytics.get_popular_queries(limit=10)

    # Get recent queries
    recent = analytics.get_recent_queries(hours=24, limit=20)

    # Get performance summary
    perf = analytics.get_performance_summary(hours=24)

    # Get cache stats
    cache_stats = query_cache.get_stats()

    return template('static/analytics.tpl',
                    popular=popular,
                    recent=recent,
                    performance=perf,
                    cache_stats=cache_stats)

# Serving static files
@app.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')


@app.error(404)
def error404(error):
    return "<body style=\"text-align: center;\"><h1>Error: 404 (Page not found)</h1><a href=\"/\">Return to EUREKA! Homepage</a></body>"


@app.error(405)
def error405(error):
    return "<body style=\"text-align: center;\"><h1>Error: 405 (HTTP method not allowed)</h1><a href=\"/\">Return to EUREKA! Homepage</a></body>"


if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCED SEARCH ENGINE STARTING")
    print("=" * 60)
    print("\nInnovative Backend Features:")
    print("  1. Advanced Ranking (TF-IDF + PageRank + Multi-Signal)")
    print("  2. Query Result Caching (LRU with TTL)")
    print("  3. Multi-Word Search Support")
    print("  4. Query Analytics Tracking")
    print("  5. Search Result Snippets")
    print("\nServer running at http://localhost:{}/".format(PORT))
    print("Analytics dashboard at http://localhost:{}/analytics".format(PORT))
    print("=" * 60)
    print()

    bottle.run(app=appWithSessions, host='0.0.0.0', port=PORT, debug=False)
