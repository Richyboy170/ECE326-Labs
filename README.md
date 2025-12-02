# EUREKA! Search Engine

A progressive web search engine built across three lab assignments for ECE326. This project demonstrates the evolution from a simple keyword analyzer to a fully-functional search engine with web crawling, PageRank algorithm, and user authentication.

## What This Website Does

EUREKA! is a Google-inspired search engine that crawls web pages, indexes content, ranks results using the PageRank algorithm, and provides a clean search interface for users to find relevant documents.

### Progressive Development

The project is built in three stages, each adding more sophisticated features:

#### Lab 1: Keyword Analysis Tool
- **Simple search interface** that analyzes user queries
- **Word frequency counter** that tracks most common search terms
- **In-memory statistics** showing top 20 words across all queries
- **Port:** 8081

#### Lab 2: Authenticated Search with User Tracking
- **Google OAuth 2.0 authentication** for user login/logout
- **Personalized search history** tracking last 10 unique words per user
- **Persistent storage** using JSON files
- **Session management** with Beaker middleware
- **AWS deployment** on EC2 (3.80.127.131:8080)
- **Port:** 8080

#### Lab 3: Full-Featured Search Engine (Main Website)
- **Web crawler** that recursively crawls and indexes websites
- **PageRank algorithm** for intelligent result ranking
- **SQLite database** for persistent data storage
- **Inverted index** for fast search queries
- **Pagination** with 5 results per page
- **Clean UI** with Google-inspired design
- **Port:** 8080

#### Lab 4: Enhanced Search Engine with Innovative Backend Features
- **Advanced Multi-Signal Ranking** (TF-IDF + PageRank + Title Match + Font Size)
- **LRU Query Caching** with TTL for 10-50x faster response times
- **Multi-Word Search** with AND/OR query support
- **Real-Time Analytics** tracking queries, clicks, and performance
- **Contextual Snippets** with query term highlighting
- **Analytics Dashboard** at `/analytics` endpoint
- **One-Click AWS Deployment** with automated scripts
- **Response Time:** 3-5ms (cached), 80-200ms (uncached)
- **Port:** 8080

## Lab 3 Architecture (Complete Search Engine)

### Core Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  urls.txt   │────▶│  crawler.py  │────▶│ storage.py  │────▶│ SQLite DB    │
│ (seed URLs) │     │ (web crawler)│     │ (DB layer)  │     │ (persistent) │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                            │                                        │
                            │                                        │
                            ▼                                        ▼
                    ┌──────────────┐                        ┌──────────────┐
                    │ pagerank.py  │◀───────────────────────│ Link Graph   │
                    │ (ranking)    │                        │              │
                    └──────────────┘                        └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ frontend.py  │◀──────── User Search Query
                    │ (web server) │
                    └──────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │ Search Results│
                    │ (HTML page)   │
                    └──────────────┘
```

### How It Works

1. **Indexing Phase:**
   - `crawler.py` reads seed URLs from `urls.txt`
   - Recursively crawls web pages using BeautifulSoup4
   - Extracts text content with font-size weighting (h1-h5, bold, strong)
   - Builds lexicon of unique words and inverted index
   - Captures link graph from anchor tags
   - `pagerank.py` computes PageRank scores based on link structure
   - All data stored in SQLite database via `storage.py`

2. **Search Phase:**
   - User enters search query in web interface
   - `frontend.py` queries the inverted index for matching documents
   - Results sorted by PageRank score (highest first)
   - Displays paginated results with titles, URLs, and scores

### Database Schema

```sql
Lexicon
├── word_id (INTEGER PRIMARY KEY)
└── word (TEXT)

DocumentIndex
├── doc_id (INTEGER PRIMARY KEY)
├── url (TEXT)
├── title (TEXT)
└── page_rank (REAL)

InvertedIndex
├── word_id (INTEGER)
├── doc_id (INTEGER)
└── font_size (INTEGER)

LinkGraph
├── from_doc_id (INTEGER)
└── to_doc_id (INTEGER)
```

## Technologies Used

| Component | Technology |
### Quick Deploy to AWS

Deploy both Lab2 and Lab3 to AWS EC2 instances in one command:

```bash
# Install deployment tools
pip install boto3 python-dotenv

# Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials

# Deploy both labs to EC2
python aws_ec2_installer.py --lab both --action all
```

### Run Performance Benchmarks

Compare Lab2 vs Lab3 performance:

```bash
# Run comprehensive benchmark suite
python benchmark_comparison.py \
    --lab2-url http://YOUR_LAB2_IP:8080 \
    --lab3-url http://YOUR_LAB3_IP:8080

# Results saved to BENCHMARK_RESULTS.md
```

### Available Tools

| Tool | Purpose | Documentation |
|------|---------|---------------|
| `aws_ec2_installer.py` | Automated EC2 deployment | [Quick Start](QUICKSTART.md) |
| `benchmark_comparison.py` | Performance benchmarking | [Full Guide](AWS_DEPLOYMENT_GUIDE.md) |
| `BENCHMARK_COMPARISON.md` | Test structure analysis | Included in repo |

### Key Features

- ✅ **One-command deployment** to AWS EC2
- ✅ **Automatic dependency installation** on instances
- ✅ **Comprehensive benchmarking** with ApacheBench
- ✅ **Detailed comparison reports** (Lab2 vs Lab3)
- ✅ **Resource monitoring** (CPU, memory, network)
- ✅ **Cost-effective** (AWS Free Tier eligible)

### Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute deployment guide
- **[AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)** - Complete deployment manual
- **[BENCHMARK_COMPARISON.md](BENCHMARK_COMPARISON.md)** - Test analysis

## 🎯 Lab 4: One-Click AWS Deployment

**NEW:** Fully automated deployment scripts for instant AWS deployment!

### Quick Deploy Lab 4

Deploy your enhanced search engine to AWS with a single command:

```bash
# 1. Configure AWS credentials
cd Lab4
cp aws_credentials.env.template aws_credentials.env
# Edit aws_credentials.env with your AWS keys

# 2. Deploy to AWS
python aws_deploy.py
```

The script automatically:
- ✅ Creates fresh EC2 instance with unique keypair
- ✅ Copies all application files (frontend, backend, databases)
- ✅ Installs dependencies (Python packages)
- ✅ Starts the search engine
- ✅ Returns public URL and instance details

### Terminate Instance

```bash
python aws_terminate.py <instance_id>
```

### Documentation

- **[Lab4/README_DEPLOYMENT.md](Lab4/README_DEPLOYMENT.md)** - Complete deployment guide
- **[Lab4/README_LAB4_FEATURES.md](Lab4/README_LAB4_FEATURES.md)** - Feature documentation

## Getting Started

### Prerequisites

```bash
pip install beautifulsoup4 bottle urllib3
```

For Lab 2 (OAuth):
```bash
pip install beaker google-auth google-auth-oauthlib google-auth-httplib2
```

### Running Lab 3 (Complete Search Engine)

1. **Build the search index:**
   ```bash
   cd Lab3
   python crawler.py
   ```
   This will:
   - Crawl websites from `urls.txt`
   - Build the lexicon and inverted index
   - Create the link graph
   - Compute PageRank scores
   - Store everything in `search_engine.db`

2. **Start the web server:**
   ```bash
   python frontend.py
   ```

3. **Access the search engine:**
   - Open your browser to `http://localhost:8080`
   - Enter a search query
   - View ranked results!

### Running Lab 2 (Authenticated Search)

1. **Configure OAuth credentials:**
   - Create `credentials.json` with Google OAuth 2.0 credentials
   - Set redirect URI to `http://localhost:8080/oauth2callback`

2. **Start the server:**
   ```bash
   cd Lab2
   python backend.py
   ```

3. **Access at:** `http://localhost:8080`

### Running Lab 1 (Keyword Analyzer)

```bash
cd Lab1
python server_starter.py
```

Access at: `http://localhost:8081`

## Using the Website

Once you have the search engine running (Lab 3), here's how to get the best results:

### Basic Usage

1. **Navigate to the homepage:** `http://localhost:8080`
2. **Enter your search query** in the search box
3. **Press Enter** or click the search button
4. **Browse results** ranked by PageRank score

### Recommended Search Queries

The search engine works best with **single keyword queries** that match the content you've crawled. Here are example queries based on typical crawled content:

#### General Queries
```
python        # Find pages about Python programming
algorithm     # Discover algorithm-related content
database      # Search for database topics
security      # Find security-related pages
network       # Network and connectivity topics
```

#### Technical Topics
```
javascript    # Web development content
machine       # Machine learning topics
cloud         # Cloud computing pages
api           # API documentation and guides
tutorial      # Learning resources
```

#### Academic Content
```
research      # Research papers and studies
course        # Course materials
lecture       # Lecture notes
university    # Academic institutions
student       # Student resources
```

### Tips for Best Results

1. **Use single words:** The search extracts the first word from your query
   - Good: `python`
   - Also works: `python programming` (searches for "python")

2. **Match indexed content:** Results depend on what URLs you've crawled
   - Check `urls.txt` to see what sites are indexed
   - Re-run `crawler.py` to add more content

3. **Understand PageRank ordering:** Higher-ranked pages appear first
   - Pages with more incoming links rank higher
   - Authority pages rise to the top

4. **Use pagination:** Navigate through results with page numbers
   - 5 results per page
   - Check multiple pages for comprehensive results

5. **Case-sensitive search:** Current implementation matches case
   - `Python` ≠ `python`
   - Use lowercase for common terms

### Customizing Your Search Index

To search different content:

1. **Edit `urls.txt`** with your desired seed URLs:
   ```
   https://en.wikipedia.org/wiki/Python_(programming_language)
   https://docs.python.org/3/
   https://www.example.com/tutorials
   ```

2. **Re-run the crawler:**
   ```bash
   cd Lab3
   python crawler.py
   ```

3. **Restart the server:**
   ```bash
   python frontend.py
   ```

4. **Search your new content!**

### Understanding Search Results

Each result displays:
- **Title:** Page title from HTML `<title>` tag
- **URL:** Full web address of the page
- **PageRank Score:** Numerical ranking (higher = more authoritative)

### Database Statistics

The homepage shows:
- **Total documents** indexed
- **Total words** in lexicon
- **Database size** and location

## Features

### Search Capabilities
- Fast keyword search using inverted index
- PageRank-based result ranking
- Pagination (5 results per page)
- Database statistics display

### Crawler Features
- Recursive web crawling with depth control
- Font-size weighting for content importance
- Stop word filtering
- 3-second timeout per page
- Link graph extraction

### User Interface
- Clean, Google-inspired design
- Responsive search form
- Clear result presentation with titles and URLs
- Page navigation controls
- Error handling (404, 405, 500)

## Project Structure

```
ECE326-Labs/
├── Lab1/                         # Keyword analysis tool
│   ├── server_starter.py         # Web server
│   └── README.md
├── Lab2/                         # Authenticated search
│   ├── backend.py                # Main server with OAuth
│   ├── frontend.py               # Web frontend
│   ├── userData.json             # User data storage
│   └── README.md
├── Lab3/                         # Full search engine
│   ├── crawler.py                # Web crawler
│   ├── pagerank.py               # PageRank algorithm
│   ├── storage.py                # Database layer
│   ├── frontend.py               # Web interface
│   ├── urls.txt                  # Seed URLs
│   ├── search_engine.db          # SQLite database (generated)
│   └── README.md
├── Lab4/                         # 🆕 Enhanced search engine
│   ├── frontend.py               # Enhanced web interface
│   ├── ranking.py                # 🆕 TF-IDF + Multi-signal ranking
│   ├── cache.py                  # 🆕 LRU cache with TTL
│   ├── analytics.py              # 🆕 Query analytics and tracking
│   ├── snippets.py               # 🆕 Contextual snippet generation
│   ├── crawler.py                # Web crawler (from Lab3)
│   ├── pagerank.py               # PageRank algorithm (from Lab3)
│   ├── storage.py                # Database layer (from Lab3)
│   ├── aws_deploy.py             # 🆕 One-click deployment script
│   ├── aws_terminate.py          # 🆕 Instance termination script
│   ├── aws_credentials.env.template  # 🆕 Credentials template
│   ├── search_engine.db          # Main database (generated)
│   ├── analytics.db              # Analytics database (generated)
│   ├── static/                   # Templates and CSS
│   ├── README_DEPLOYMENT.md      # Deployment documentation
│   ├── README_LAB4_FEATURES.md   # Feature documentation
│   └── README_for_running_code.md
├── aws_ec2_installer.py          # AWS EC2 deployment automation
├── benchmark_comparison.py       # Performance benchmarking tool
├── requirements-deployment.txt   # Deployment tool dependencies
├── .env.example                  # Environment config template
├── QUICKSTART.md                 # 5-minute deployment guide
├── AWS_DEPLOYMENT_GUIDE.md       # Complete deployment manual
├── BENCHMARK_COMPARISON.md       # Test structure analysis
├── BENCHMARK_RESULTS.md          # Generated benchmark report
└── README.md                     # This file
```

## Educational Context

This project is part of the **University of Toronto ECE326 course** and demonstrates:

- **Web Development:** Building web applications with Python and Bottle
- **Database Design:** Schema design and SQL optimization
- **Information Retrieval:** Inverted index and search algorithms
- **Graph Algorithms:** PageRank implementation
- **Web Scraping:** HTML parsing with BeautifulSoup
- **Authentication:** OAuth 2.0 integration
- **Cloud Deployment:** AWS EC2 hosting
- **Session Management:** Beaker middleware

## How PageRank Works

PageRank is Google's original algorithm for ranking web pages. The implementation:

1. **Analyzes the link graph** where each page is a node
2. **Computes importance scores** based on incoming links
3. **Uses damping factor** (0.85) to simulate random browsing
4. **Iterates 20 times** to converge on stable scores
5. **Normalizes scores** to sum to 1.0
6. **Ranks results** by these scores

Formula: `PR(A) = (1-d) + d * Σ(PR(Ti)/C(Ti))`

Where:
- `PR(A)` = PageRank of page A
- `d` = damping factor (0.85)
- `Ti` = pages that link to A
- `C(Ti)` = number of outbound links from Ti

## Search Algorithm

1. User enters query (e.g., "python")
2. Extract first word from query
3. Query inverted index for word_id
4. Retrieve all documents containing the word
5. Sort by PageRank score (descending)
6. Paginate results (5 per page)
7. Display with title, URL, and score

## Notes

- **Lab 3** is the main/complete website
- **Lab 2** adds authentication but removes crawling
- **Lab 1** is the foundational prototype
- Data persists across server restarts (Lab 2 & 3)
- Search is case-sensitive in current implementation
- Crawler respects 3-second timeout per page

## License

Educational project for ECE326 course at University of Toronto.

## Authors

ECE326 Students - University of Toronto
