import json, os
from dotenv import load_dotenv
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import httplib2
from beaker.middleware import SessionMiddleware
import bottle
from bottle import run, get, post, request, response, route, static_file, Bottle
PORT=8080

# Load the keys * Note that ID and SECRET are "xxxxxxxxxx" for submission, used to be loaded from .env
load_dotenv()
ID = os.getenv("GOOGLE_CLIENT_ID")
SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
#ID = "xxxxxxxxxx"
#SECRET = "xxxxxxxxxx"

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

    # Update HTML based on whether the user is logged in or not
    if email:
        buttonText = "Log out"
        actionURL = "/logout"
        loginStatus = f"Logged in as: {email}"
    else:
        buttonText = "Log in with Google"
        actionURL = "/login"
        loginStatus = "Not logged in"

    return bottle.template('static/index.html', loginStatus=loginStatus, actionURL = actionURL, buttonText = buttonText)

# If login button pressed, this function will redirect to google login screen
@app.route('/login', method='GET')
def loginRedirect():
    
    # Redirects to google login screen  * Note that client_secret.json is hidden
    flow = flow_from_clientsecrets("client_secret.json",
        scope='https://www.googleapis.com/auth/plus.me  \
        https://www.googleapis.com/auth/userinfo.email',
        redirect_uri='http://localhost:8080/redirect'
        # redirect_uri='http://3.80.127.131.sslip.io:8080/redirect'
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
@app.post("/")
def process_query():
    
    # Get email from session
    session = request.environ.get('beaker.session')
    email = session.get('email', None)

    # Process the form data
    query = request.forms.get('keywords')

    # Update HTML based on whether the user is logged in or not
    if email:
        buttonText = "Log out"
        actionURL = "/logout"
        loginStatus = f"Logged in as: {email}"
    else:
        buttonText = "Log in with Google"
        actionURL = "/login"
        loginStatus = "Not logged in"

    #Start with the opening for the HTML string
    displayHTML = f"<html lang=\"en\"><head><meta charset=\"UTF-8\"><title>EUREKA!</title></head>"
    displayHTML += f"<div style=\"text-align: right;\"><p>{loginStatus}</p><form action=\"{actionURL}\" method=\"get\"><button type=\"submit\">{buttonText}</button></form></div>"
    displayHTML += f"<body style=\"text-align: center;\">"
    # Display the original input
    displayHTML += f"<h2> Search for: '{query}' </h2>"
    
    # Convert to lowercase as the words are case-insensitive
    # Extract all the words from the input into a list
    # Display the number of words
    keywordList = query.lower().split()
    displayHTML += f"<p> Number of words entered: {len(keywordList)} </p>"

    # Create a dictionary with the words as keys and the # of appearences as values
    # This is just for the specific query
    keywordDict = updateAppearences(keywordList, {})

    # Display the current query's words and their respective number of appearences in a table
    displayHTML += "<h4> Word Count </h4>"
    displayHTML += "<table id=”results” style=\"margin: auto; width: 25%; text-align: center; border: 1px solid black;\">"
    displayHTML += "<tr><th> Word </th><th> # Appearences </th></tr>"
    for word, appearences in keywordDict.items():
        displayHTML += f"<tr><td>{word}</td><td>{appearences}</td></tr>"
    displayHTML += "</table>"

    # If user is logged in, save the query data and show the last ten used words
    if email:

        # Get the data of the user
        currUserData = userData.setdefault(email, {"keywordUsage": {}, "recentWords": []})

        # Update the user data with this query's words
        for word in keywordList:
            
            # Update dictionary of words and appearences
            currUserData["keywordUsage"][word] = currUserData["keywordUsage"].get(word, 0) + 1

            # For recent words, we want no repeats and want to have the most recent time they used the word so we must remove the word if it shows up again now
            if(word in currUserData["recentWords"]):
                currUserData["recentWords"].remove(word)

            # Add the word to the recent word list
            currUserData["recentWords"].append(word)

            # We want only 10 words so kick out oldest word if it gets above 10
            if len(currUserData["recentWords"]) > 10:
                currUserData["recentWords"].pop(0)

        # Update JSON with data
        saveDataToJSON(userData)

        # Display the table of the last 10 used words
        displayHTML += "<h4> Last 10 Used Words (from last-typed to oldest with no repeats) </h4>"
        displayHTML += "<table id=history style=\"margin: auto; width: 25%; text-align: center; border: 1px solid black;\">"
        displayHTML += "<tr><th> Word </th><th> # Appearences </th></tr>"
        for word in currUserData["recentWords"][::-1]:
            displayHTML += f"<tr><td>{word}</td><td>{currUserData['keywordUsage'][word]}</td></tr>"
        displayHTML += "</table>"

    else:
        # if not logged in show that history not available
        displayHTML += "<h4> Login with Google to see last 10 used words </h4>"

    # Close HTML String
    displayHTML += "</body></html>"

    return displayHTML

# Serves Logo for query page
@app.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')

run(app = appWithSessions, host='0.0.0.0', port=PORT)