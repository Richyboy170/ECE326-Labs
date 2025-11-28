"""
Enhanced Search Engine Frontend

This enhanced frontend integrates innovative backend features:
1. Advanced ranking system (TF-IDF + PageRank + multi-signal)
2. Query result caching for improved performance
3. Multi-word search support
4. Query analytics tracking
5. Search result snippets

This provides a much better search experience than the basic version.
"""

import json
import os
import time
from dotenv import load_dotenv
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
from beaker.middleware import SessionMiddleware
import bottle
from bottle import run, get, post, request, response, route, error, template, static_file, Bottle

# Import our enhanced backend modules
from storage import SearchEngineDB
from ranking import AdvancedRanker
from cache import get_query_cache
from analytics import get_analytics
from snippets import get_snippet_generator

PORT = 8080

DB_FILE = "search_engine.db"
ANALYTICS_DB_FILE = "analytics.db"
RESULTS_PER_PAGE = 5

# Initialize global instances
query_cache = get_query_cache(capacity=500, ttl=1800)  # Cache 500 queries for 30 mins
analytics = get_analytics(ANALYTICS_DB_FILE)
snippet_gen = get_snippet_generator()


def get_db():
    """Get database connection"""
    return SearchEngineDB(DB_FILE)


# Load the keys
load_dotenv()
ID = os.getenv("GOOGLE_CLIENT_ID")
SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

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

# File to store user data
DATA_FILE = "userData.json"


def loadDataFromJSON():
    """Load data from user data JSON"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def saveDataToJSON(data):
    """Save data to user data JSON"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


userData = loadDataFromJSON()


@app.route('/')
def home():
    """Query screen displayed when /"""

    # Get email from session
    session = request.environ.get('beaker.session')
    email = session.get('email', None)
    email = None

    # Update HTML based on whether the user is logged in or not
    if email:
        buttonText = "Log out"
        actionURL = "/logout"
        loginStatus = f"Logged in as: {email}"
    else:
        buttonText = "Log in with Google"
        actionURL = "/login"
        loginStatus = "Not logged in"

    return bottle.template('static/index.tpl', loginStatus=loginStatus, actionURL=actionURL, buttonText=buttonText)


@app.route('/login', method='GET')
def loginRedirect():
    """If login button pressed, this function will redirect to google login screen"""

    # Check if client_secret.json exists
    if not os.path.exists("client_secret.json"):
        return "<body style=\"text-align: center;\"><h1>Error: client_secret.json not found</h1><p>Google OAuth is not configured. Login functionality is disabled.</p><a href=\"/\">Return to EUREKA! Homepage</a></body>"

    # Redirects to google login screen
    flow = flow_from_clientsecrets("client_secret.json",
                                    scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
                                    redirect_uri='http://localhost:8080/redirect'
                                    )
    uri = flow.step1_get_authorize_url()
    bottle.redirect(str(uri))


@app.route('/redirect')
def redirect_page():
    """Handles google login screen"""

    code = request.query.get("code", "")
    scope = ['profile', 'email']
    flow = OAuth2WebServerFlow(ID, SECRET, scope=scope,
                                redirect_uri="http://localhost:8080/redirect")
    credentials = flow.step2_exchange(code)
    token = credentials.id_token["sub"]

    http = httplib2.Http()
    http = credentials.authorize(http)
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']

    session = request.environ.get('beaker.session')
    session['email'] = user_email
    session['token'] = token
    session.save()

    if user_email not in userData:
        userData[user_email] = {"keywordUsage": {}, "recentWords": []}
        saveDataToJSON(userData)

    bottle.redirect("/")


@app.route('/logout')
def logout():
    """If logout button pressed, handles logout"""
    session = request.environ.get('beaker.session')
    session.delete()
    bottle.redirect('/')


@app.route("/search")
def process_query():
    """
    Enhanced search with multi-word support, caching, analytics, and advanced ranking
    """

    # Get email from session
    session = request.environ.get('beaker.session')
    email = session.get('email', None)
    email = None

    # Update HTML based on whether the user is logged in or not
    if email:
        buttonText = "Log out"
        actionURL = "/logout"
        loginStatus = f"Logged in as: {email}"
    else:
        buttonText = "Log in with Google"
        actionURL = "/login"
        loginStatus = "Not logged in"

    # Start timing for analytics
    start_time = time.time()

    # Get query - NOW SUPPORTS MULTI-WORD QUERIES!
    query = request.query.keywords or ""
    query = query.strip()

    # Get the current page number (default is 1)
    page = int(request.query.page or 1)
    per_page = RESULTS_PER_PAGE

    # Check cache first
    cached_results = query_cache.get_results(query, page, per_page)

    if cached_results is not None:
        # Cache hit!
        urls, total_pages, cache_hit = cached_results
        response_time_ms = (time.time() - start_time) * 1000

        # Log to analytics
        analytics.log_query(query, len(urls) * total_pages, response_time_ms, user_ip=request.remote_addr)

        return template('static/resultPage_enhanced.tpl',
                        loginStatus=loginStatus,
                        actionURL=actionURL,
                        buttonText=buttonText,
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

            # Generate snippets for results
            # Note: In a full implementation, you'd store page content
            # For now, we'll use the title as a simple snippet
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
                    loginStatus=loginStatus,
                    actionURL=actionURL,
                    buttonText=buttonText,
                    urls=page_urls,
                    query=query,
                    page=page,
                    total_pages=total_pages,
                    cache_hit=False,
                    response_time=f"{response_time_ms:.2f}ms")


@app.route('/analytics')
def show_analytics():
    """Display analytics dashboard"""

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


@app.route('/static/<filename>')
def server_static(filename):
    """Serves static files"""
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
