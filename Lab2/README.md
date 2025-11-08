# README
IP ADDRESS: http://3.83.233.24:8080/

Instance ID:  i-0378f9759aaa7d8d4
Public IP:    3.83.233.24
Key file:     ece326-keypair.pem

# This is our .env file (keys are hidden):

## AWS Credentials
AWS_ACCESS_KEY=xxxxxxxxxxx

AWS_SECRET_KEY=xxxxxxxxxxx

## AWS Configuration
AWS_REGION=us-east-1

KEY_NAME=ece326-keypair

SECURITY_GROUP_NAME=ece326-group5

INSTANCE_TYPE=t3.micro

UBUNTU_AMI=ami-0c398cb65a93047f2

## Google Client
GOOGLE_CLIENT_ID=xxxxxxxxxxx

GOOGLE_CLIENT_SECRET=xxxxxxxxxxx


# Lab2 - EUREKA! Search Engine

A web-based search query application with Google OAuth authentication that tracks user keyword usage and search history.

## Overview

EUREKA! is a keyword search interface that allows users to:
- Submit search queries and view word count statistics
- Log in with Google OAuth to track search history
- View the last 10 unique words searched (for logged-in users)
- See cumulative keyword usage statistics across all searches

## Prerequisites

- Python 3.x
- AWS Account (for deployment only)
- Google Cloud Platform account with OAuth 2.0 credentials

## Setup Instructions

### 1. Install Dependencies

```bash
cd Lab2
pip install -r requirements.txt
```

### 2. Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable Google+ API and Google OAuth2 API
4. Create OAuth 2.0 credentials (Web application type)
5. Add authorized redirect URIs:
   - `http://localhost:8080/redirect` (for local development)
   - `http://YOUR_PUBLIC_IP:8080/redirect` (for deployment)
6. Download the credentials as `client_secret.json` and place it in the Lab2 folder

### 3. Create Environment Variables

Create a `.env` file in the Lab2 directory with the following content:

```bash
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# AWS Credentials (only needed for deployment)
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=us-east-1
KEY_NAME=ece326-keypair
SECURITY_GROUP_NAME=ece326-group5
INSTANCE_TYPE=t3.micro
UBUNTU_AMI=ami-0c398cb65a93047f2
```

## Running Locally

### Start the Application

```bash
python frontend.py
```

The application will start on `http://localhost:8080`

### Using the Application

1. Open your browser and navigate to `http://localhost:8080`
2. Enter keywords in the search box and click "Search"
3. View the word count statistics for your query
4. (Optional) Click "Log in with Google" to track your search history
5. When logged in, see your last 10 unique words and their cumulative usage

### Features

**Without Login:**
- Submit search queries
- View word counts for the current query

**With Google Login:**
- All features above, plus:
- Last 10 unique words searched (most recent first, no duplicates)
- Cumulative count of how many times each word has been used across all searches
- Persistent storage of search history in `userData.json`

## Deploying to AWS EC2

### 1. Deploy an EC2 Instance

```bash
python backend.py
```

This script will:
- Create an EC2 key pair
- Set up a security group with necessary ports (22, 80, 8080, 8081)
- Launch a t3.micro Ubuntu instance
- Display connection information

### 2. Connect to Your Instance

```bash
ssh -i ece326-keypair.pem ubuntu@YOUR_PUBLIC_IP
```

### 3. Copy Files to Instance

```bash
scp -i ece326-keypair.pem frontend.py backend.py requirements.txt .env client_secret.json ubuntu@YOUR_PUBLIC_IP:~/
scp -i ece326-keypair.pem -r static ubuntu@YOUR_PUBLIC_IP:~/
```

### 4. Set Up the Instance

SSH into the instance and run:

```bash
sudo apt update
sudo apt install python3-pip -y
pip install -r requirements.txt
```

### 5. Update Redirect URI

Edit `frontend.py` and update line 89 to use your public IP:

```python
redirect_uri='http://YOUR_PUBLIC_IP:8080/redirect'
```

Also update your Google OAuth credentials to include this redirect URI.

### 6. Run the Application

```bash
python3 frontend.py
```

Access the application at `http://YOUR_PUBLIC_IP:8080`

## Testing

Run the test suite:

```bash
python test_frontend.py
```

The tests verify:
- Word counting functionality
- Dictionary update operations
- Session management
- Data persistence

## File Structure

```
Lab2/
├── frontend.py          # Main web application (Bottle framework)
├── backend.py           # AWS EC2 deployment script
├── requirements.txt     # Python dependencies
├── test_frontend.py     # Unit tests
├── .env                 # Environment variables (not in git)
├── client_secret.json   # Google OAuth credentials (not in git)
├── userData.json        # User search history data (created at runtime)
├── static/
│   ├── index.html      # Main page template
│   └── EurekaLogo.jpg  # Application logo
└── README.md           # This file
```

## Port Configuration

The application runs on port **8080** by default. If you need to change this, modify the `PORT` variable in `frontend.py`.

## Security Notes

- Never commit `.env` or `client_secret.json` to version control
- The `.gitignore` file is configured to exclude sensitive files
- For production deployment, consider using HTTPS
- Restrict security group rules to specific IP ranges when possible

## Troubleshooting

**OAuth redirect error:**
- Ensure your redirect URI in Google Cloud Console matches exactly
- Check that `client_secret.json` is in the correct location

**Session data not persisting:**
- Check that the `./sessions` directory is writable
- Verify `userData.json` is being created in the working directory

**AWS deployment issues:**
- Verify AWS credentials are correct in `.env`
- Check that the security group allows inbound traffic on port 8080
- Ensure the Ubuntu AMI ID is valid for your region

## Additional Resources

- Lab specification: `ECE326-Lab2.pdf`
- Google OAuth 2.0 documentation: https://developers.google.com/identity/protocols/oauth2
- Bottle framework documentation: https://bottlepy.org/
- AWS EC2 documentation: https://docs.aws.amazon.com/ec2/
