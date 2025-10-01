from bottle import run, get, post, request, route, static_file
PORT=8081

test = 0

@get("/")
def home():
    return static_file('index.html', root='static')

@post("/")
def process_query():
    # Process the form data
    keywords = request.forms.get('keywords')

    # KEEP THIS ORIGINAL KEYWORD STRING TO DISPLAY
    # SHOW: "SEARCH FOR 'KEYWORDS'"
    
    # SEPERATE INTO LIST OF WORDS USING ASSIGNMENT FUNC

    # STORE NUMBER OF WORDS (IE LENGTH OF LIST)
    # SHOW: "TOTAL NUMBER OF KEYWORDS: 'TOTALNUMWORDS'"

    # LOOP THROUGH LIST AND CREATE DICTIONARY FOR NUM WORD APPEARNCES IN THIS SEARCH
    # DICTIONARY CAN BE LOCAL TO THIS FUNCTION
    # DICTIONARY USES KEYWORDS AS KEYS AND # OCCURRENCES AS VALUES
    #           *** CASE INSENSITIVE ***

    # SHOW THIS QUERY'S KEYWORD DICTIONARY AS A HTML TABLE
    
    # COMBINE THIS INFO WITH A GLOBAL MASTER DICTIONARY THAT STORES ALL APPEARENCES

    # IDENTIFY THE TOP 20 WORDS AND INSERT INTO HTML TABLE
    global test
    test += 1

    return f"<html><table id=”results”><tr><td>the</td><td>2</td></tr><tr><td>lab</td><td>3</td></tr></table></html>"

run(host='localhost', port=PORT)