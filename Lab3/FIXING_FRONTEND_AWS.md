# Fixing frontend.py for AWS Deployment

## Overview

Your friend's frontend.py has several critical issues that prevent it from working on AWS. This document explains each issue and how to fix it.

## Critical Issues Found

### 🔴 Issue 1: Server Only Listens on localhost (Line 196)

**Problem:**
```python
bottle.run(app=appWithSessions, host='localhost', port=PORT, debug=False)
```

**Why it fails on AWS:**
- `host='localhost'` only accepts connections from the same machine
- AWS instances need to accept external connections from the internet
- Your browser cannot connect from outside the EC2 instance

**Fix:**
```python
bottle.run(app=appWithSessions, host='0.0.0.0', port=PORT, debug=False)
```

**Location:** `frontend.py:196`

---

### 🔴 Issue 2: Email Variable Hardcoded to None (Lines 73 & 147)

**Problem:**
```python
session = request.environ.get('beaker.session')
email = session.get('email', None)
email = None  # <-- This line breaks everything!
```

**Why it fails:**
- The code retrieves the email from the session
- Then immediately overrides it with `email = None`
- This completely breaks the Google OAuth login functionality
- Users can never be logged in, even after successful authentication

**Fix:**
Remove the `email = None` line:
```python
session = request.environ.get('beaker.session')
email = session.get('email', None)
# Remove: email = None
```

**Locations:** `frontend.py:73` and `frontend.py:147`

---

### 🔴 Issue 3: Hardcoded Redirect URI for localhost (Lines 95 & 108)

**Problem:**
```python
# Line 95
redirect_uri='http://localhost:8080/redirect'

# Line 108
redirect_uri="http://localhost:8080/redirect"
```

**Why it fails on AWS:**
- Google OAuth requires the redirect URI to match your actual server address
- `localhost:8080` only works on your local machine
- On AWS, you need to use your EC2 instance's public IP (e.g., `98.80.72.155:8080`)
- Google will reject the authentication because the redirect URI doesn't match

**Fix:**
```python
# Line 95
redirect_uri='http://98.80.72.155:8080/redirect'

# Line 108
redirect_uri="http://98.80.72.155:8080/redirect"
```

**Additional Step Required:**
You must also update your Google Cloud Console OAuth settings to include this redirect URI in the authorized redirect URIs list.

**Locations:** `frontend.py:95` and `frontend.py:108`

---

### 🟡 Issue 4: Missing client_secret.json File (Line 92)

**Problem:**
```python
flow = flow_from_clientsecrets("client_secret.json", ...)
```

**Why it fails:**
- The file `client_secret.json` is required for Google OAuth
- This file contains your Google OAuth credentials
- Without it, the login functionality will crash immediately

**Fix:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Add authorized redirect URI: `http://98.80.72.155:8080/redirect`
7. Download the JSON file and rename it to `client_secret.json`
8. Copy it to your Lab3 directory

**Location:** `frontend.py:92`

---

### 🟡 Issue 5: Missing .env File (Lines 22-24)

**Problem:**
```python
load_dotenv()
ID = os.getenv("GOOGLE_CLIENT_ID")
SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
```

**Why it fails:**
- The code expects a `.env` file with Google credentials
- Without it, `ID` and `SECRET` will be `None`
- OAuth authentication will fail

**Fix:**
Create a `.env` file in the Lab3 directory:
```bash
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

Get these values from your `client_secret.json` file:
- `GOOGLE_CLIENT_ID` = the "client_id" field
- `GOOGLE_CLIENT_SECRET` = the "client_secret" field

**Location:** `frontend.py:22-24`

---

### 🟡 Issue 6: Missing sessions Directory (Line 33)

**Problem:**
```python
session_opts = {
    'session.type': 'file',
    'session.data_dir': './sessions',
    ...
}
```

**Why it fails:**
- Beaker sessions need a directory to store session data
- If `./sessions` doesn't exist, the app will crash on first login attempt

**Fix:**
```bash
mkdir -p sessions
```

**Location:** `frontend.py:33`

---

### 🟢 Issue 7: Unused userData.json Functionality (Lines 38-64)

**Problem:**
The code has a complete implementation for tracking user keyword usage:
- `loadDataFromJSON()` function (lines 42-46)
- `saveDataToJSON()` function (lines 49-51)
- `updateAppearences()` function (lines 57-64)
- User data initialization (lines 126-128)

**But it's never actually used!**

**Why it's a problem:**
- Dead code that adds complexity
- Creates unnecessary files (userData.json)
- Gives false impression of functionality that doesn't exist

**Options:**
1. **Remove it** if you don't need keyword tracking
2. **Implement it properly** in the search function to actually track queries

**Location:** `frontend.py:38-64, 126-128`

---

## Step-by-Step Fix Guide

### For Simple Search Engine (Without Google OAuth)

If you just want a working search engine without login functionality:

1. **Remove all Google OAuth code** (lines 1-4, 21-24, 30-64, 87-138)
2. **Simplify the templates** to remove login/logout buttons
3. **Change host binding:**
   ```python
   bottle.run(app=app, host='0.0.0.0', port=8080, debug=False)
   ```

This gives you a simple, working search engine like the demo frontend.py.

### For Full OAuth Implementation

If you want to keep Google OAuth:

1. **Fix host binding** (Line 196):
   ```python
   bottle.run(app=appWithSessions, host='0.0.0.0', port=PORT, debug=False)
   ```

2. **Remove email override** (Lines 73 & 147):
   - Delete the line: `email = None`

3. **Update redirect URIs** (Lines 95 & 108):
   ```python
   redirect_uri='http://98.80.72.155:8080/redirect'
   ```

4. **Create client_secret.json** from Google Cloud Console

5. **Create .env file:**
   ```bash
   GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-secret
   ```

6. **Create sessions directory:**
   ```bash
   mkdir sessions
   ```

7. **Update Google Cloud Console:**
   - Add `http://98.80.72.155:8080/redirect` to authorized redirect URIs

8. **Deploy to AWS:**
   ```bash
   # Copy files
   scp -i ece326-keypair.pem frontend.py ubuntu@98.80.72.155:~/
   scp -i ece326-keypair.pem storage.py ubuntu@98.80.72.155:~/
   scp -i ece326-keypair.pem search_engine.db ubuntu@98.80.72.155:~/
   scp -i ece326-keypair.pem client_secret.json ubuntu@98.80.72.155:~/
   scp -i ece326-keypair.pem .env ubuntu@98.80.72.155:~/
   scp -r -i ece326-keypair.pem static ubuntu@98.80.72.155:~/

   # SSH and run
   ssh -i ece326-keypair.pem ubuntu@98.80.72.155
   mkdir -p sessions
   nohup python3 frontend.py > frontend.log 2>&1 &
   ```

---

## Comparison: Demo frontend.py vs Friend's frontend.py

### Demo frontend.py (Simple & Works)
✅ No authentication required
✅ Simple and straightforward
✅ No external dependencies (OAuth, sessions)
✅ `host='0.0.0.0'` - accepts external connections
✅ Works on AWS out of the box

### Friend's frontend.py (Complex & Broken)
❌ Requires Google OAuth setup
❌ Multiple missing files (client_secret.json, .env)
❌ Email hardcoded to None (breaks login)
❌ Redirect URI hardcoded to localhost
❌ `host='localhost'` - doesn't accept external connections
❌ Unused code for userData tracking
❌ Missing sessions directory

---

## Quick Fix: Minimal Changes to Make It Work

If you want to make the **minimal changes** to get it working on AWS:

### Edit frontend.py:

1. **Line 73:** Delete `email = None`
2. **Line 147:** Delete `email = None`
3. **Line 95:** Change to `redirect_uri='http://98.80.72.155:8080/redirect'`
4. **Line 108:** Change to `redirect_uri="http://98.80.72.155:8080/redirect"`
5. **Line 196:** Change to `host='0.0.0.0'`

### On AWS EC2:
```bash
# Create required directory
mkdir -p sessions

# Create .env file (use your actual Google credentials)
cat > .env << EOF
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
EOF

# Upload client_secret.json from Google Cloud Console
# (Do this from your local machine)
scp -i ece326-keypair.pem client_secret.json ubuntu@98.80.72.155:~/

# Install missing dependencies
pip3 install oauth2client google-api-python-client httplib2 beaker python-dotenv

# Run the server
nohup python3 frontend.py > frontend.log 2>&1 &
```

---

## Recommended Approach

**For this lab, I recommend using the simple demo frontend.py** because:

1. ✅ It works immediately on AWS
2. ✅ No complex OAuth setup required
3. ✅ No external dependencies
4. ✅ Focuses on the search engine functionality (what the lab is about)
5. ✅ Easier to debug and maintain

**The Google OAuth version adds unnecessary complexity** for a search engine lab assignment. OAuth is great for production apps with user accounts, but it's overkill for a course project.

---

## Testing Your Fix

After applying the fixes, test:

1. **Can you access the site externally?**
   ```
   http://98.80.72.155:8080
   ```

2. **Check if server is listening:**
   ```bash
   sudo netstat -tlnp | grep 8080
   # Should show: 0.0.0.0:8080 (not 127.0.0.1:8080)
   ```

3. **Test search functionality:**
   - Enter a keyword and click search
   - Verify results appear
   - Test pagination

4. **If using OAuth, test login:**
   - Click "Log in with Google"
   - Should redirect to Google
   - After authentication, should redirect back to your site
   - Should show "Logged in as: your-email@gmail.com"

---

## Common Errors and Solutions

### Error: "Connection refused" when accessing from browser
**Cause:** `host='localhost'` in bottle.run()
**Fix:** Change to `host='0.0.0.0'`

### Error: "client_secret.json not found"
**Cause:** Missing OAuth credentials file
**Fix:** Download from Google Cloud Console

### Error: OAuth redirect URI mismatch
**Cause:** Google doesn't recognize your redirect URI
**Fix:** Add `http://YOUR_IP:8080/redirect` to Google Cloud Console authorized URIs

### Error: User always shows as "Not logged in"
**Cause:** `email = None` hardcoded
**Fix:** Remove that line

### Error: "sessions directory not found"
**Cause:** Missing sessions directory for Beaker
**Fix:** `mkdir -p sessions`

---

## Files Needed for AWS Deployment

### Simple Version (No OAuth):
```
frontend.py
storage.py
search_engine.db
static/
  ├── index.html
  ├── resultPage.tpl
  └── EurekaLogo.jpg
```

### OAuth Version:
```
frontend.py
storage.py
search_engine.db
client_secret.json     ← Required
.env                   ← Required
sessions/              ← Directory (create with mkdir)
static/
  ├── index.html
  ├── resultPage.tpl
  └── EurekaLogo.jpg
```

---

## Summary

The main reason your friend's frontend.py doesn't work on AWS is:

1. **🔴 CRITICAL:** `host='localhost'` prevents external access
2. **🔴 CRITICAL:** `email = None` breaks OAuth login
3. **🔴 CRITICAL:** Hardcoded redirect URIs won't work with AWS IP
4. **🟡 MISSING FILES:** client_secret.json, .env, sessions directory

**Recommendation:** Use the simple demo frontend.py for this lab, or make the minimal fixes listed above.

---

## Need Help?

If you're still having issues:

1. Check the logs:
   ```bash
   tail -f frontend.log
   ```

2. Verify the process is running:
   ```bash
   ps aux | grep frontend.py
   ```

3. Check which host/port it's listening on:
   ```bash
   sudo netstat -tlnp | grep 8080
   ```

4. Test from the EC2 instance itself:
   ```bash
   curl http://localhost:8080
   ```

---

**Created:** 2025-01-09
**For:** ECE326 Lab 3 - Search Engine
**Issue:** Friend's frontend.py not working on AWS EC2
