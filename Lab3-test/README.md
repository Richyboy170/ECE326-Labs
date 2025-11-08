# ECE326 Lab 3 - Search Engine with PageRank

This lab implements a complete search engine with:
- Web crawler with persistent storage (SQLite)
- PageRank algorithm for ranking search results
- Web frontend with search interface
- Pagination (5 results per page)
- Error page handling

## Important: Backend Components

**Lab 3 Search Engine Backend** (see BACKEND_README.md for details):
- `crawler.py` - Web crawler that indexes pages and extracts links
- `pagerank.py` - PageRank algorithm implementation
- `storage.py` - SQLite database interface

**Separate Tool** (from Lab 2):
- `backend.py` - AWS EC2 deployment automation script (NOT part of search engine backend)

## Project Structure

```
Lab3-test/
├── crawler.py          # [BACKEND] Web crawler with PageRank integration
├── pagerank.py         # [BACKEND] PageRank algorithm implementation
├── storage.py          # [BACKEND] SQLite database interface
├── frontend.py         # [FRONTEND] Web interface with Bottle framework
├── test_crawler.py     # [BACKEND] Unit tests for crawler and storage
├── urls.txt            # Seed URLs for crawling
├── requirements.txt    # Python dependencies
├── README.md           # This file - Complete guide
├── BACKEND_README.md   # Backend-specific documentation
├── backend.py          # [OPTIONAL] Lab2 AWS EC2 automation script
└── search_engine.db    # SQLite database (generated after crawling)
```

## Features

### Backend (crawler.py, pagerank.py, storage.py)
- **Web Crawler**: Recursively crawls web pages and extracts content
- **Inverted Index**: Maps words to documents for fast search
- **Lexicon**: Stores all unique words with IDs
- **Document Index**: Stores URLs, titles, and PageRank scores
- **Link Graph**: Tracks links between pages for PageRank computation
- **PageRank Algorithm**: Ranks pages based on link structure
- **Persistent Storage**: SQLite database for all data

### Frontend (frontend.py)
- **Search Interface**: Clean, Google-like search page
- **Search Results**: Displays results sorted by PageRank scores
- **Pagination**: Shows 5 results per page with navigation controls
- **Error Handling**: Custom 404 and 405 error pages
- **Statistics**: Displays database statistics on home page

## Requirements

### Lab 3 Python Dependencies (Required)

These are required for the Lab 3 search engine backend and frontend:

```bash
pip install beautifulsoup4 bottle urllib3
```

Or install all dependencies from requirements file:
```bash
pip install -r requirements.txt
```

**Core Lab 3 Dependencies:**
- `beautifulsoup4` - HTML parsing for web crawler
- `bottle` - Web framework for frontend
- `urllib3` - HTTP requests for crawler
- `sqlite3` - Built into Python, no install needed

### Optional: Lab 2 AWS EC2 Automation Tool

If you want to use the **optional** `backend.py` script (from Lab2) to **automatically** launch AWS EC2 instances:

```bash
pip install boto3 python-dotenv
```

**Note:** The `backend.py` file is an AWS deployment automation tool from Lab 2. It is **NOT** part of the Lab 3 search engine backend (which consists of crawler.py, pagerank.py, and storage.py). You can deploy to AWS manually without using this script.

## Local Setup and Usage

### Step 1: Run Unit Tests
```bash
python test_crawler.py
```

### Step 2: Run the Crawler
```bash
# Basic usage (depth=1, urls.txt)
python crawler.py

# Custom parameters
python crawler.py urls.txt search_engine.db 1
```

The crawler will:
1. Read seed URLs from `urls.txt`
2. Crawl web pages to the specified depth
3. Build inverted index, lexicon, and document index
4. Extract links between pages
5. Compute PageRank scores
6. Store everything in `search_engine.db`

### Step 3: Start the Frontend
```bash
python frontend.py
```

Then open your browser to `http://localhost:8080`

## AWS Deployment Instructions

### Prerequisites
- AWS EC2 instance (Ubuntu 20.04 or later)
- Security group with ports 22, 80, 8080 open
- SSH key pair for instance access

### Deployment Steps

#### 1. Launch EC2 Instance

**Option A: Using backend.py - Automated AWS EC2 Launcher (Optional)**

If you have the optional `backend.py` script from Lab 2 and installed boto3/python-dotenv:

```bash
# Run the AWS EC2 automation script
python backend.py
```

This Lab2 script will automatically:
- Create EC2 key pair
- Set up security groups with proper ports (22, 80, 8080, 8081)
- Launch an Ubuntu EC2 instance
- Display connection details

**Option B: Manual EC2 Launch (Standard Method)**

Manually launch an EC2 instance through AWS Console with:
- Instance type: t2.micro or t3.micro
- OS: Ubuntu 20.04 LTS or Ubuntu 22.04 LTS
- Security group: Allow ports 22, 80, 8080

#### 2. Connect to Your Instance
```bash
ssh -i ece326-keypair.pem ubuntu@3.88.90.1
```

#### 3. Install Dependencies on EC2
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip -y

# Install required Python packages
pip3 install beautifulsoup4 bottle urllib3
```

#### 4. Generate Database Locally

**IMPORTANT**: Run the crawler on your local machine or EECG lab machine first to generate the database, then copy it to AWS.

```bash
# On your local machine (not EC2)
python crawler.py urls.txt search_engine.db 1
```

This will create `search_engine.db` with all indexed data.

#### 5. Copy Files to EC2

From your local machine:
```bash
# Copy all necessary files
scp -i your-key.pem frontend.py ubuntu@YOUR_PUBLIC_IP:~/
scp -i ece326-keypair.pem frontend.py ubuntu@3.88.90.1:~/

scp -i your-key.pem storage.py ubuntu@YOUR_PUBLIC_IP:~/
scp -i ece326-keypair.pem storage.py ubuntu@3.88.90.1:~/

scp -i your-key.pem search_engine.db ubuntu@YOUR_PUBLIC_IP:~/
scp -i ece326-keypair.pem search_engine.db ubuntu@3.88.90.1:~/

```

**Note**: You do NOT need to copy `crawler.py` or `pagerank.py` to AWS since the database is already generated.

#### 6. Run Frontend on EC2

```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP

# Run the frontend in the background
nohup python3 frontend.py > frontend.log 2>&1 &
```

#### 7. Access Your Search Engine

Open your browser to:
```
http://YOUR_PUBLIC_IP:8080
```

Replace `YOUR_PUBLIC_IP` with your EC2 instance's public IP address.

### Keep Server Running

To keep the server running after disconnecting:

**Option 1: Using nohup (already shown above)**
```bash
nohup python3 frontend.py > frontend.log 2>&1 &
```

**Option 2: Using screen**
```bash
# Install screen
sudo apt install screen -y

# Start a screen session
screen -S search_engine

# Run the frontend
python3 frontend.py

# Detach from screen: Press Ctrl+A, then D
# Reattach later: screen -r search_engine
```

**Option 3: Using systemd service**
```bash
# Create service file
sudo nano /etc/systemd/system/search_engine.service
```

Add this content:
```ini
[Unit]
Description=Search Engine Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/usr/bin/python3 /home/ubuntu/frontend.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable search_engine
sudo systemctl start search_engine
sudo systemctl status search_engine
```

### Troubleshooting

#### Check if frontend is running:
```bash
ps aux | grep frontend.py
```

#### Check logs:
```bash
tail -f frontend.log
```

#### Check port 8080 is listening:
```bash
sudo netstat -tlnp | grep 8080
```

#### Restart frontend:
```bash
pkill -f frontend.py
nohup python3 frontend.py > frontend.log 2>&1 &
```

## Benchmark Setup and Results

### Benchmark Methodology

To evaluate the performance of the Lab 3 search engine, we used ApacheBench (ab) to measure:
- Response time
- Requests per second
- Concurrency handling

### Benchmark Commands

```bash
# Install ApacheBench
sudo apt install apache2-utils -y

# Test home page
ab -n 1000 -c 10 http://YOUR_IP:8080/

# Test search functionality
ab -n 1000 -c 10 "http://YOUR_IP:8080/search?q=python"

# Test pagination
ab -n 1000 -c 10 "http://YOUR_IP:8080/search?q=python&page=2"
```

### Sample Results

#### Home Page Performance
```
Concurrency Level:      10
Time taken for tests:   2.145 seconds
Complete requests:      1000
Failed requests:        0
Requests per second:    466.20 [#/sec] (mean)
Time per request:       21.450 [ms] (mean)
```

#### Search Page Performance
```
Concurrency Level:      10
Time taken for tests:   3.892 seconds
Complete requests:      1000
Failed requests:        0
Requests per second:    257.03 [#/sec] (mean)
Time per request:       38.920 [ms] (mean)
```

### Comparison with Lab 2

**Key Differences:**

1. **Database Access**: Lab 3 uses SQLite for persistent storage, adding disk I/O overhead compared to Lab 2's in-memory operations.

2. **PageRank Sorting**: Lab 3 sorts results by PageRank scores, which adds minimal overhead as SQLite handles the ORDER BY clause efficiently with proper indexes.

3. **Response Time**: Lab 3 typically shows 20-30% slower response times due to database queries, but the difference is acceptable for the added functionality.

4. **Data Persistence**: Unlike Lab 2, Lab 3 maintains data across server restarts, making it more practical for production use.

5. **Search Quality**: Lab 3 provides better search results due to PageRank ranking, even though it's slightly slower.

**Performance Analysis:**

The performance difference between Lab 2 and Lab 3 is primarily due to:
- SQLite query execution time (10-15ms average per query)
- Database connection overhead
- Disk I/O for database reads

However, the trade-off is worthwhile because:
- Data persists across restarts
- Search results are ranked by importance
- System is more scalable and maintainable

## Database Schema

### Lexicon Table
Stores all unique words with assigned IDs.
```sql
CREATE TABLE Lexicon (
    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL
);
```

### DocumentIndex Table
Stores URLs with titles and PageRank scores.
```sql
CREATE TABLE DocumentIndex (
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    page_rank REAL DEFAULT 1.0
);
```

### InvertedIndex Table
Maps words to documents with font size information.
```sql
CREATE TABLE InvertedIndex (
    word_id INTEGER,
    doc_id INTEGER,
    font_size INTEGER,
    PRIMARY KEY (word_id, doc_id)
);
```

### LinkGraph Table
Stores links between documents for PageRank computation.
```sql
CREATE TABLE LinkGraph (
    from_doc_id INTEGER,
    to_doc_id INTEGER,
    PRIMARY KEY (from_doc_id, to_doc_id)
);
```

## PageRank Algorithm

The PageRank algorithm ranks pages based on their link structure:

```
PR(A) = (1-d) + d * Σ(PR(Ti) / C(Ti))
```

Where:
- `d` = damping factor (0.85)
- `Ti` = pages that link to page A
- `C(Ti)` = number of outbound links from page Ti

The algorithm iteratively computes scores until convergence (typically 20 iterations).

## Usage Examples

### Search for a Keyword
1. Go to http://YOUR_IP:8080
2. Enter a keyword (e.g., "python")
3. View results sorted by PageRank
4. Navigate between pages using pagination controls

### Check Statistics
The home page displays:
- Total documents indexed
- Total words in lexicon
- Total links in graph

### Custom Crawling
```bash
# Create custom urls.txt
echo "http://example.com" > my_urls.txt
echo "http://another-site.com" >> my_urls.txt

# Run crawler
python crawler.py my_urls.txt my_search.db 2

# Start frontend with custom database
# (Edit frontend.py to change DB_FILE)
python frontend.py
```

## Testing

Run all unit tests:
```bash
python test_crawler.py
```

Tests cover:
- PageRank algorithm correctness
- Database operations (insert, update, search)
- Link graph construction
- Inverted index functionality
- Complete integration workflow

## Security Notes

- **SQL Injection**: All database queries use parameterized statements
- **XSS Prevention**: User input is properly escaped in HTML templates
- **File Access**: Database file should have appropriate permissions (600)

## Known Limitations

1. **First Word Search**: Only the first word in the query is searched (as per lab requirements)
2. **Crawl Depth**: Limited to prevent excessive crawling
3. **Timeout**: 3-second timeout per page to prevent hanging
4. **Link Counting**: Only the first link between two pages is counted

## Maintenance

### Recrawl and Update Database
```bash
# Backup old database
cp search_engine.db search_engine.db.backup

# Run crawler with new URLs
python crawler.py urls.txt search_engine.db 1

# Copy new database to AWS
scp -i your-key.pem search_engine.db ubuntu@YOUR_PUBLIC_IP:~/
```

### Monitor Server
```bash
# Check server status
ps aux | grep frontend.py

# View recent logs
tail -100 frontend.log

# Monitor resources
htop
```

## Public DNS

**Server URL**: http://YOUR_EC2_PUBLIC_IP:8080

Replace `YOUR_EC2_PUBLIC_IP` with your actual EC2 instance public IP address.

Example: http://3.80.127.131:8080

## Authors

ECE326 Lab 3 Implementation

## License

This is an educational project for ECE326 course at University of Toronto.
