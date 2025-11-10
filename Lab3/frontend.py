"""
Search Engine Frontend with Pagination

This frontend provides a web interface for searching indexed documents.
Features:
- Search query interface
- Results sorted by PageRank scores
- Pagination (5 results per page)
- Error page handling (404 errors)
- Google OAuth integration (disabled by default)
"""

from bottle import Bottle, run, request, response, static_file
from storage import SearchEngineDB
import os
import json
from dotenv import load_dotenv
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
from beaker.middleware import SessionMiddleware

# Configuration
DB_FILE = "search_engine.db"
RESULTS_PER_PAGE = 5
PORT = 8080

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


def get_db():
    """Get database connection"""
    return SearchEngineDB(DB_FILE)


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


# Load data from JSON
userData = loadDataFromJSON()


def updateAppearences(list, dict):
    """Given a list of words, update the dictionary with each appearance of the word"""
    for word in list:
        if word not in dict:
            dict[word] = 1
        else:
            dict[word] += 1
    return dict


@app.route('/')
def home():
    """Display the search query page"""

    # Get email from session
    session = request.environ.get('beaker.session')
    email = session.get('email', None)
    email = None  # Disabled for now

    # Update HTML based on whether the user is logged in or not
    if email:
        buttonText = "Log out"
        actionURL = "/logout"
        loginStatus = f"Logged in as: {email}"
    else:
        buttonText = "Log in with Google"
        actionURL = "/login"
        loginStatus = "Not logged in"

    html = f"""<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <title>EUREKA!</title>
</head>

<div style="text-align: right;">
  <p>{loginStatus}</p>
  <form action="{actionURL}" method="get"><button type="submit">{buttonText}</button></form>
</div>

<body style="text-align: center;">
  <img src="/static/EurekaLogo.jpg" alt="Euereka Logo" width="150" height="120">
  <h1>
    EUREKA!
  </h1>
  <form action="/search" method="get">
    <label>
      Search:
      <input name="keywords" type="text" />
    </label>
    <input value="Submit" type="submit" />
  </form>
</body>

</html>
"""
    return html


@app.route('/login', method='GET')
def loginRedirect():
    """Redirect to Google login screen"""

    # Redirects to google login screen  * Note that client_secret.json is hidden
    flow = flow_from_clientsecrets("client_secret.json",
        scope='https://www.googleapis.com/auth/plus.me  \
        https://www.googleapis.com/auth/userinfo.email',
        redirect_uri='http://localhost:8080/redirect'
    )
    uri = flow.step1_get_authorize_url()
    response.redirect(str(uri))


@app.route('/redirect')
def redirect_page():
    """Handle Google login redirect"""

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

    response.redirect("/")


@app.route('/logout')
def logout():
    """Handle logout"""
    session = request.environ.get('beaker.session')
    session.delete()
    response.redirect('/')


@app.route("/search")
def search():
    """Handle search queries with pagination"""

    # Get email from session
    session = request.environ.get('beaker.session')
    email = session.get('email', None)
    email = None  # Disabled for now

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

    # Get urls from database (urls come back as a list of tuples of (url, page title, pagerank))
    try:
        with get_db() as db:
            urls = db.search_word(query, limit=1000)
    except Exception as e:
        return error_page(f"Database error: {e}", 500)

    # Calculate pagination
    total_results = len(urls)
    total_pages = (total_results + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE or 1

    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages

    # Display only select number of URLs (in our case 5)
    start = (page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    pageUrls = urls[start:end]

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Results for "{query}"</title>
</head>
<body>

    <div style="text-align: right;">
        <p>{loginStatus}</p>
        <form action="{actionURL}" method="get"><button type="submit">{buttonText}</button></form>
    </div>

    <form action="/search" method="get">
        <img src="/static/EurekaLogo.jpg" alt="Euereka Logo" width="50" height="40">
        <input type="text" name="keywords" value="{query}">
        <input type="submit" value="Search">
    </form>

    <h2>Results for "{query}"</h2>
"""

    if not pageUrls:
        html += """
    <p>No results found.</p>
"""
    else:
        html += """
    <ul>
"""
        for url, title, pr in pageUrls:
            html += f"""        <p><a href="{url}">{title}</a> (Page rank: {pr})</p>
"""
        html += """    </ul>
"""

    # Pagination controls
    html += """
    <div style="margin-top:20px;">
"""
    if page > 1:
        html += f"""        <a href="/search?keywords={query}&page={page-1}">Previous</a>
"""

    html += f"""        Page {page} of {total_pages}
"""

    if page < total_pages:
        html += f"""        <a href="/search?keywords={query}&page={page+1}">Next</a>
"""

    html += """    </div>

    <p><a href="/">Back to Home</a></p>
</body>
</html>
"""

    return html


def error_page(message="Page not found", code=404):
    """Generate error page"""
    response.status = code
    html = f"""<body style="text-align: center;">
<h1>Error: {code} ({message})</h1>
<a href="/">Return to EUREKA! Homepage</a>
</body>"""
    return html


@app.error(404)
def error404(error):
    """Handle 404 errors"""
    return error_page("Page not found", 404)


@app.error(405)
def error405(error):
    """Handle 405 Method Not Allowed errors"""
    return error_page("HTTP method not allowed", 405)


@app.error(500)
def error500(error):
    """Handle 500 Internal Server errors"""
    return error_page("Internal server error", 500)


@app.route('/static/<filename>')
def serve_static(filename):
    """Serve static files"""
    return static_file(filename, root='./static')


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

    run(app=appWithSessions, host='localhost', port=PORT, debug=False)
