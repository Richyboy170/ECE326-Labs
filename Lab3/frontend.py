"""
Search Engine Frontend with Pagination
<<<<<<< HEAD

This frontend provides a web interface for searching indexed documents.
Features:
- Search query interface
- Results sorted by PageRank scores
- Pagination (5 results per page)
- Error page handling (404 errors)
"""

from bottle import Bottle, run, request, response, template, static_file
from storage import SearchEngineDB
import os

app = Bottle()

# Configuration
=======

This frontend provides a web interface for searching indexed documents.
Features:
- Search query interface with OAuth authentication
- Results sorted by PageRank scores
- Pagination (5 results per page)
- Error page handling (404, 405 errors)
"""

import json
import os
from dotenv import load_dotenv
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
from beaker.middleware import SessionMiddleware
import bottle
from bottle import run, get, post, request, response, route, error, template, static_file, Bottle
from storage import SearchEngineDB

# Configuration
PORT = 8080
>>>>>>> e167d5993730cd9e8312273d2983d65998610605
DB_FILE = "search_engine.db"
RESULTS_PER_PAGE = 5
PORT = 8080


def get_db():
    """Get database connection"""
    return SearchEngineDB(DB_FILE)


@app.route('/')
def home():
<<<<<<< HEAD
    """Display the search query page"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EUREKA! Search Engine</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #4285f4;
                text-align: center;
                font-size: 48px;
                margin-bottom: 30px;
            }
            .search-box {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }
            input[type="text"] {
                width: 500px;
                padding: 12px 20px;
                font-size: 16px;
                border: 1px solid #ddd;
                border-radius: 24px 0 0 24px;
                outline: none;
            }
            input[type="text"]:focus {
                border-color: #4285f4;
                box-shadow: 0 1px 6px rgba(66, 133, 244, 0.3);
            }
            button {
                padding: 12px 30px;
                font-size: 16px;
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 0 24px 24px 0;
                cursor: pointer;
            }
            button:hover {
                background-color: #357ae8;
            }
            .info {
                text-align: center;
                color: #666;
                margin-top: 20px;
            }
            .stats {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-top: 30px;
            }
            .stats h3 {
                margin-top: 0;
                color: #333;
            }
            .stats p {
                margin: 5px 0;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>EUREKA!</h1>
            <form action="/search" method="GET" class="search-box">
                <input type="text" name="q" placeholder="Enter search keyword..." required autofocus>
                <button type="submit">Search</button>
            </form>
            <div class="info">
                <p>Enter a keyword to search indexed documents</p>
            </div>
            {{STATS}}
        </div>
    </body>
    </html>
    """

    # Get database statistics
=======

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

    return bottle.template('static/index.html', loginStatus=loginStatus, actionURL=actionURL, buttonText=buttonText)

# If login button pressed, this function will redirect to google login screen
@app.route('/login', method='GET')
def loginRedirect():

    # Redirects to google login screen  * Note that client_secret.json is hidden
    flow = flow_from_clientsecrets("client_secret.json",
        scope='https://www.googleapis.com/auth/plus.me  \
        https://www.googleapis.com/auth/userinfo.email',
        redirect_uri='http://localhost:8080/redirect'
    )
    uri = flow.step1_get_authorize_url()
    bottle.redirect(str(uri))

# Handles google login screen
@app.route('/redirect')
def redirect_page():

    # Handles google login
    code = request.query.get("code", "")
    scope = ['profile', 'email']
    flow = OAuth2WebServerFlow(ID, SECRET, scope=scope,
        redirect_uri="http://localhost:8080/redirect")
    credentials = flow.step2_exchange(code)
    token = credentials.id_token["sub"]

    http = httplib2.Http()
    http = credentials.authorize(http)
    # Get user email
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    user_email = user_document['email']

    # Save email and token to the session
    session = request.environ.get('beaker.session')
    session['email'] = user_email
    session['token'] = token
    session.save()

    # Initialize user data if new
    if user_email not in userData:
        userData[user_email] = {"keywordUsage": {}, "recentWords": []}
        saveDataToJSON(userData)

    bottle.redirect("/")

# If logout button pressed, handles logout
@app.route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    session.delete()

    bottle.redirect('/')

# When form is submitted, query is processed and screen will display tables with updated info based on query
@app.route("/search")
def process_query():

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

    # Get query (we only use the first word)
    query = request.query.keywords or ""
    if query != "":
        query = query.split()[0]

    # Get the current page number (default is 1)
    page = int(request.query.page or 1)
    perPage = RESULTS_PER_PAGE

    # Get urls from database (urls come back as a list of tuples of (url, page title, pagerank))
>>>>>>> e167d5993730cd9e8312273d2983d65998610605
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
<<<<<<< HEAD
        stats_html = f'<div class="info"><p style="color: red;">Database not found. Please run the crawler first.</p></div>'
=======
        return error_page(f"Database error: {e}", 500)
>>>>>>> e167d5993730cd9e8312273d2983d65998610605

    return html.replace('{{STATS}}', stats_html)

<<<<<<< HEAD
=======
    return template('static/resultPage.tpl', loginStatus=loginStatus, actionURL=actionURL, buttonText=buttonText, urls=pageUrls, query=query, page=page, total_pages=totalPages)
>>>>>>> e167d5993730cd9e8312273d2983d65998610605

@app.route('/search')
def search():
    """Handle search queries with pagination"""
    query = request.query.get('q', '').strip().lower()
    page = int(request.query.get('page', 1))

    if not query:
        return home()

    # Extract first word from query (as per lab requirements)
    words = query.split()
    search_word = words[0] if words else ''

    if not search_word:
        return home()

    # Search the database
    try:
        with get_db() as db:
            all_results = db.search_word(search_word, limit=1000)
    except Exception as e:
        return error_page(f"Database error: {e}")

    # Calculate pagination
    total_results = len(all_results)
    total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages

    start_idx = (page - 1) * RESULTS_PER_PAGE
    end_idx = start_idx + RESULTS_PER_PAGE
    page_results = all_results[start_idx:end_idx]

    # Generate HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Results for "{search_word}" - EUREKA!</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 20px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #4285f4;
                font-size: 32px;
                margin: 0 0 15px 0;
            }}
            .search-box {{
                display: flex;
                margin-bottom: 10px;
            }}
            input[type="text"] {{
                flex: 1;
                padding: 10px 15px;
                font-size: 14px;
                border: 1px solid #ddd;
                border-radius: 24px 0 0 24px;
                outline: none;
            }}
            button {{
                padding: 10px 25px;
                font-size: 14px;
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 0 24px 24px 0;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #357ae8;
            }}
            .results-info {{
                color: #666;
                margin-top: 10px;
            }}
            .result {{
                background-color: white;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .result-title {{
                font-size: 18px;
                color: #1a0dab;
                text-decoration: none;
                font-weight: normal;
            }}
            .result-title:hover {{
                text-decoration: underline;
            }}
            .result-url {{
                color: #006621;
                font-size: 14px;
                margin: 5px 0;
            }}
            .result-pagerank {{
                color: #999;
                font-size: 12px;
            }}
            .no-results {{
                background-color: white;
                padding: 40px;
                text-align: center;
                border-radius: 8px;
            }}
            .pagination {{
                background-color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px;
                margin-top: 20px;
            }}
            .pagination a {{
                display: inline-block;
                padding: 8px 12px;
                margin: 0 2px;
                background-color: #f8f9fa;
                color: #4285f4;
                text-decoration: none;
                border-radius: 4px;
            }}
            .pagination a:hover {{
                background-color: #e8e9ea;
            }}
            .pagination .current {{
                background-color: #4285f4;
                color: white;
            }}
            .pagination .disabled {{
                color: #ccc;
                pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1><a href="/" style="text-decoration: none; color: #4285f4;">EUREKA!</a></h1>
            <form action="/search" method="GET" class="search-box">
                <input type="text" name="q" value="{query}" required>
                <button type="submit">Search</button>
            </form>
            <div class="results-info">
                About {total_results} results for "{search_word}"
                {f" (Page {page} of {total_pages})" if total_pages > 0 else ""}
            </div>
        </div>
    """

    if total_results == 0:
        html += """
        <div class="no-results">
            <h2>No results found</h2>
            <p>Try different keywords or check the spelling</p>
            <p><a href="/">Back to home</a></p>
        </div>
        """
    else:
        # Display results
        for url, title, pagerank in page_results:
            display_title = title if title else url
            html += f"""
            <div class="result">
                <a href="{url}" class="result-title" target="_blank">{display_title}</a>
                <div class="result-url">{url}</div>
                <div class="result-pagerank">PageRank: {pagerank:.6f}</div>
            </div>
            """

        # Pagination controls
        if total_pages > 1:
            html += '<div class="pagination">'

            # Previous button
            if page > 1:
                html += f'<a href="/search?q={query}&page={page-1}">Previous</a>'
            else:
                html += '<a class="disabled">Previous</a>'

            # Page numbers
            start_page = max(1, page - 2)
            end_page = min(total_pages, page + 2)

            if start_page > 1:
                html += f'<a href="/search?q={query}&page=1">1</a>'
                if start_page > 2:
                    html += '<span>...</span>'

            for p in range(start_page, end_page + 1):
                if p == page:
                    html += f'<a class="current">{p}</a>'
                else:
                    html += f'<a href="/search?q={query}&page={p}">{p}</a>'

            if end_page < total_pages:
                if end_page < total_pages - 1:
                    html += '<span>...</span>'
                html += f'<a href="/search?q={query}&page={total_pages}">{total_pages}</a>'

            # Next button
            if page < total_pages:
                html += f'<a href="/search?q={query}&page={page+1}">Next</a>'
            else:
                html += '<a class="disabled">Next</a>'

            html += '</div>'

    html += """
    </body>
    </html>
    """

    return html


def error_page(message="Page not found", code=404):
    """Generate error page"""
    response.status = code
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Error {code} - EUREKA!</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 100px auto;
                padding: 20px;
                text-align: center;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 60px 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #ea4335;
                font-size: 72px;
                margin: 0;
            }}
            h2 {{
                color: #333;
                margin: 20px 0;
            }}
            p {{
                color: #666;
                margin: 15px 0;
            }}
            a {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 30px;
                background-color: #4285f4;
                color: white;
                text-decoration: none;
                border-radius: 24px;
            }}
            a:hover {{
                background-color: #357ae8;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{code}</h1>
            <h2>Oops! {message}</h2>
            <p>The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.</p>
            <a href="/">Go to Home Page</a>
        </div>
    </body>
    </html>
    """
    return html


def error_page(message="Page not found", code=404):
    """Generate error page"""
    response.status = code
    return f'<body style="text-align: center;"><h1>Error: {code} ({message})</h1><a href="/">Return to EUREKA! Homepage</a></body>'

@app.error(404)
def error404(error):
<<<<<<< HEAD
    """Handle 404 errors"""
    return error_page("Page not found", 404)


@app.error(405)
def error405(error):
    """Handle 405 Method Not Allowed errors"""
    return error_page("Method not allowed", 405)


@app.error(500)
def error500(error):
    """Handle 500 Internal Server errors"""
    return error_page("Internal server error", 500)


@app.route('/static/<filename>')
def serve_static(filename):
    """Serve static files"""
    return static_file(filename, root='./static')


=======
    return error_page("Page not found", 404)

@app.error(405)
def error405(error):
    return error_page("HTTP method not allowed", 405)

@app.error(500)
def error500(error):
    return error_page("Internal server error", 500)

>>>>>>> e167d5993730cd9e8312273d2983d65998610605
if __name__ == "__main__":
    print("=" * 60)
    print("ECE326 Lab 3 - Search Engine Frontend")
    print("=" * 60)
    print(f"Database: {DB_FILE}")
    print(f"Results per page: {RESULTS_PER_PAGE}")
    print(f"Port: {PORT}")
    print("=" * 60)

    if not os.path.exists(DB_FILE):
        print("\nWARNING: Database file not found!")
        print(f"Please run the crawler first to generate {DB_FILE}")
        print("=" * 60)

    print(f"\nStarting server at http://localhost:{PORT}")
    print("Press Ctrl+C to stop\n")

<<<<<<< HEAD
    run(app, host='0.0.0.0', port=PORT, debug=True)
=======
    bottle.run(app=appWithSessions, host='0.0.0.0', port=PORT, debug=False)
>>>>>>> e167d5993730cd9e8312273d2983d65998610605
