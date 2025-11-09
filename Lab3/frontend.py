"""
Search Engine Frontend with Pagination

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
DB_FILE = "search_engine.db"
RESULTS_PER_PAGE = 5

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

# Function that returns data from user data JSON
def loadDataFromJSON():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Function that saves data to user data JSON
def saveDataToJSON(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Load data from JSON
userData = loadDataFromJSON()

# Given a list of words, the function will update the dictionary with each appearence of the word
def updateAppearences(list, dict):
   for word in list:
       if word not in dict:
          dict[word] = 1
       else:
          dict[word] += 1

   return dict

# Query screen displayed when /
@app.route('/')
def home():

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
    try:
        with get_db() as db:
            urls = db.search_word(query, limit=1000)
    except Exception as e:
        return error_page(f"Database error: {e}", 500)

    # Display only select number of URLs (in our case 5)
    start = (page - 1) * perPage
    end = start + perPage
    pageUrls = urls[start:end]
    totalPages = (len(urls) + perPage - 1) // perPage or 1

    return template('static/resultPage.tpl', loginStatus=loginStatus, actionURL=actionURL, buttonText=buttonText, urls=pageUrls, query=query, page=page, total_pages=totalPages)

# Serves Logo for query page
@app.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')

def error_page(message="Page not found", code=404):
    """Generate error page"""
    response.status = code
    return f'<body style="text-align: center;"><h1>Error: {code} ({message})</h1><a href="/">Return to EUREKA! Homepage</a></body>'

@app.error(404)
def error404(error):
    return error_page("Page not found", 404)

@app.error(405)
def error405(error):
    return error_page("HTTP method not allowed", 405)

@app.error(500)
def error500(error):
    return error_page("Internal server error", 500)

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

    bottle.run(app=appWithSessions, host='0.0.0.0', port=PORT, debug=False)
