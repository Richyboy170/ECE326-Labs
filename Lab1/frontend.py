from bottle import run, get, post, request, route, static_file
PORT=8081

# Create a dictionary with the words as keys and the # of appearences as values
# This variable is used to store ALL keywords entered since bottle started
totalKeywordDict = {}

# Given a list of words, the function will update the dictionary with each appearence of the word
def updateAppearences(list, dict):
   for word in list:
       if word not in dict:
          dict[word] = 1
       else:
          dict[word] += 1

   return dict

# Query screen displayed when /
@get("/")
def home():
    return static_file('index.html', root='static')

# When form is submitted, query is processed and screen will display tables with updated info based on query
@post("/")
def process_query():
    # Process the form data
    query = request.forms.get('keywords')

    #Start with the opening for the HTML string
    displayHTML = "<html><body style=\"text-align: center;\">"

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
    displayHTML += "<table id='results' style=\"margin: auto; width: 25%; text-align: center; border: 1px solid black;\">"
    displayHTML += "<tr><th> Word </th><th> # Appearences </th></tr>"
    for word, appearences in keywordDict.items():
        displayHTML += f"<tr><td>{word}</td><td>{appearences}</td></tr>"
    displayHTML += "</table>"
    
    # Update the global keyword dictionary with the current query's words
    global totalKeywordDict
    updateAppearences(keywordList, totalKeywordDict)

    # Sort the total keywords dictionary and grab the top 20 used words
    # ie sort the dictionary by the values (# appearences) from highest to lowest, and take only the first 20 elements
    topTwentyKeywords = sorted(totalKeywordDict.items(), key=lambda item: item[1], reverse=True)[:20]

    # Display these top 20 words in a table
    displayHTML += "<h4> Top 20 Used Words </h4>"
    displayHTML += "<table id='history' style=\"margin: auto; width: 25%; text-align: center; border: 1px solid black;\">"
    displayHTML += "<tr><th> Word </th><th> # Appearences </th></tr>"
    for word, appearences in topTwentyKeywords:
        displayHTML += f"<tr><td>{word}</td><td>{appearences}</td></tr>"
    displayHTML += "</table>"

    # Close HTML String
    displayHTML += "</body></html>"

    return displayHTML

# Serves Logo for query page
@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')

run(host='localhost', port=PORT)