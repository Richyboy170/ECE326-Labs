# Lab 3 Backend - Web Crawler with PageRank

This document describes the backend components of the Lab 3 search engine, which implement web crawling, PageRank computation, and persistent storage.

## Overview

The backend consists of three main components:

1. **crawler.py** - Web crawler that indexes pages and extracts links
2. **pagerank.py** - PageRank algorithm implementation
3. **storage.py** - SQLite database interface for persistent storage

These components work together to:
- Crawl web pages from seed URLs
- Build inverted index, lexicon, and document index
- Extract link graph between pages
- Compute PageRank scores
- Store all data in persistent SQLite database

## Architecture

```
urls.txt (Seed URLs)
    ↓
[crawler.py]
    ├── Visits URLs Recursively
    ├── Parses HTML Pages (BeautifulSoup)
    ├── Extracts Words → Lexicon
    ├── Builds Inverted Index (word → documents)
    ├── Captures Links (anchor tags)
    └── Stores in Database
         ↓
[storage.py] - SQLite Database
    ├── Lexicon Table (word_id, word)
    ├── DocumentIndex Table (doc_id, url, title, page_rank)
    ├── InvertedIndex Table (word_id, doc_id, font_size)
    └── LinkGraph Table (from_doc_id, to_doc_id)
         ↓
[pagerank.py]
    ├── Reads Link Graph from Database
    ├── Computes PageRank Scores (iterative algorithm)
    ├── Normalizes Scores
    └── Updates Database with Scores
         ↓
search_engine.db (Ready for Frontend)
```

## Component Details

### 1. crawler.py - Web Crawler

The crawler is the main backend component that:

**Key Features:**
- Reads seed URLs from `urls.txt`
- Recursively crawls pages to specified depth
- Parses HTML using BeautifulSoup
- Extracts text content with font size weights
- Builds lexicon (all unique words)
- Creates inverted index (word → document mappings)
- **Captures link relations from anchor (`<a>`) tags** (Lab 3 requirement)
- Stores all data in SQLite database

**Important Implementation Details:**
- **Link Extraction**: The `_visit_a()` method captures links between pages from `<a href>` tags
- **First Link Only**: Only the first link between two documents is counted (as per PDF hints)
- **Font Size Weighting**: Words in headers (h1-h5) and emphasized text (b, i, strong, em) get higher weights
- **Ignored Words**: Common stop words like "the", "of", "and" are filtered out
- **Timeout**: 3-second timeout per page to prevent hanging

**Usage:**
```bash
# Basic usage (default: urls.txt, search_engine.db, depth=1)
python crawler.py

# Custom parameters
python crawler.py <url_file> <db_file> <depth>

# Example
python crawler.py urls.txt search_engine.db 1
```

**Command Line Arguments:**
- `url_file`: Path to file containing seed URLs (default: urls.txt)
- `db_file`: Path to SQLite database file (default: search_engine.db)
- `depth`: Maximum crawl depth (default: 1)

**Process Flow:**
1. Initialize database connection
2. Load seed URLs from file
3. For each URL (breadth-first):
   - Fetch and parse HTML
   - Extract title and update document
   - Parse all text content
   - Extract all outgoing links (anchor tags)
   - Store words in inverted index
   - Store links in link graph
4. Compute PageRank scores
5. Update database with scores
6. Display statistics

### 2. pagerank.py - PageRank Algorithm

Implements Google's PageRank algorithm to rank documents based on link structure.

**Algorithm:**
```
PR(A) = (1-d) + d * Σ(PR(Ti) / C(Ti))

Where:
- d = damping factor (0.85)
- Ti = pages that link to page A
- C(Ti) = number of outbound links from page Ti
```

**Key Features:**
- Iterative computation (default: 20 iterations)
- Handles pages with no outbound links
- Normalizes scores to sum to 1.0
- Returns importance score for each page

**Functions:**
- `page_rank(links, num_iterations, initial_pr)` - Computes raw PageRank scores
- `normalize_page_rank(scores)` - Normalizes scores to sum to 1.0

**Usage in Crawler:**
```python
# Get link graph from database
link_graph = db.get_link_graph()  # {doc_id: [linked_doc_ids]}

# Compute PageRank
scores = page_rank(link_graph, num_iterations=20)

# Normalize
scores = normalize_page_rank(scores)

# Update database
db.update_page_ranks(scores)
```

**Example:**
```python
# Example link structure:
# Page 1 → Page 2, Page 3
# Page 2 → Page 3
# Page 3 → Page 1

links = {
    1: [2, 3],
    2: [3],
    3: [1]
}

scores = page_rank(links)
# Result: Page 3 has highest score (receives most links)
```

### 3. storage.py - Persistent Storage Interface

Provides SQLite database interface for storing all search engine data.

**Database Schema:**

#### Lexicon Table
Stores all unique words with assigned IDs.
```sql
CREATE TABLE Lexicon (
    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE NOT NULL
);
```

#### DocumentIndex Table
Stores URLs with titles and PageRank scores.
```sql
CREATE TABLE DocumentIndex (
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT,
    page_rank REAL DEFAULT 1.0
);
```

#### InvertedIndex Table
Maps words to documents with font size information.
```sql
CREATE TABLE InvertedIndex (
    word_id INTEGER,
    doc_id INTEGER,
    font_size INTEGER,
    PRIMARY KEY (word_id, doc_id),
    FOREIGN KEY (word_id) REFERENCES Lexicon(word_id),
    FOREIGN KEY (doc_id) REFERENCES DocumentIndex(doc_id)
);
```

#### LinkGraph Table
**Stores links between documents for PageRank computation** (Lab 3 requirement).
```sql
CREATE TABLE LinkGraph (
    from_doc_id INTEGER,
    to_doc_id INTEGER,
    PRIMARY KEY (from_doc_id, to_doc_id),
    FOREIGN KEY (from_doc_id) REFERENCES DocumentIndex(doc_id),
    FOREIGN KEY (to_doc_id) REFERENCES DocumentIndex(doc_id)
);
```

**Key Methods:**
- `insert_word(word)` - Add word to lexicon, return word_id
- `insert_document(url, title)` - Add document, return doc_id
- `insert_inverted_index(word_id, doc_id, font_size)` - Link word to document
- `insert_link(from_doc_id, to_doc_id)` - Add link to graph
- `get_link_graph()` - Get complete link structure for PageRank
- `update_page_ranks(scores)` - Update PageRank scores
- `search_word(word, limit)` - Search for word, return results sorted by PageRank
- `get_statistics()` - Get database statistics

**Features:**
- Automatic duplicate handling (UNIQUE constraints)
- Indexed columns for fast queries
- Context manager support (`with` statement)
- Transaction management (automatic commit)

## Data Flow

### Phase 1: Crawling and Indexing
```
1. Read urls.txt
   ↓
2. Visit each URL
   ↓
3. For each page:
   - Extract title → Update DocumentIndex
   - Parse text → Extract words → Insert into Lexicon
   - Map words to document → Insert into InvertedIndex
   - Extract <a href> links → Insert into LinkGraph
   ↓
4. Move to next URL (breadth-first, up to max depth)
```

### Phase 2: PageRank Computation
```
1. Get link graph from database
   {doc_id: [linked_doc_ids]}
   ↓
2. Run PageRank algorithm (20 iterations)
   Compute importance score for each document
   ↓
3. Normalize scores (sum to 1.0)
   ↓
4. Update DocumentIndex.page_rank column
```

### Phase 3: Frontend Access
```
1. Frontend receives search query
   ↓
2. Query database:
   SELECT url, title, page_rank
   FROM DocumentIndex
   JOIN InvertedIndex ON doc_id
   WHERE word = 'search_term'
   ORDER BY page_rank DESC
   ↓
3. Return results to user (sorted by PageRank)
```

## Requirements Compliance (Lab 3 PDF)

### B1. PageRank Algorithm ✓
- Implemented in `pagerank.py`
- Ranks documents based on number of citations (incoming links)
- Uses iterative algorithm with damping factor 0.85

### B2. Compute PageRank Scores ✓
- **Links discovered from anchor (`<a>`) tags** - See crawler.py:162-170
- Link relations stored in LinkGraph table
- PageRank function called after crawling completes
- Scores stored in persistent storage

### B3. Persistent Storage ✓
- Uses SQLite3 database
- Stores all required data:
  - ✓ Lexicon (words with IDs)
  - ✓ Document Index (URLs, titles, PageRank scores)
  - ✓ Inverted Index (word-document mappings)
  - ✓ Link Graph (page-to-page links)

### B4. Requirements ✓
- ✓ Computes PageRank for each page visited by crawler
- ✓ Takes URLs from "urls.txt"
- ✓ Generates and stores lexicon, document index, inverted index, and PageRank scores
- ✓ All data in persistent storage (SQLite)

## Running the Backend

### Step 1: Prepare URLs
Create or edit `urls.txt` with seed URLs:
```bash
echo "http://www.eecg.toronto.edu" > urls.txt
echo "http://info.cern.ch" >> urls.txt
```

**Note**: For Lab 3 submission, database must contain data crawled from `www.eecg.toronto.edu` with depth of one (as per PDF requirements).

### Step 2: Run Unit Tests
```bash
python test_crawler.py
```

Expected output:
```
ECE326 Lab 3 - Unit Tests
==============================================================

test_simple_graph (test_crawler.TestPageRank) ... ok
test_linear_graph (test_crawler.TestPageRank) ... ok
...
All tests passed!
```

### Step 3: Run the Crawler
```bash
# Use default parameters (urls.txt, search_engine.db, depth=1)
python crawler.py

# Or specify custom parameters
python crawler.py urls.txt search_engine.db 1
```

**Expected Output:**
```
============================================================
ECE326 Lab 3 - Web Crawler with PageRank
============================================================
URL file: urls.txt
Database: search_engine.db
Crawl depth: 1
============================================================

Starting crawl with depth=1, timeout=3s
Initial URL queue size: 2

Crawling: http://www.eecg.toronto.edu (depth=0)
  Document title: Edward S. Rogers Sr. Department of Electrical & Computer...
  Number of words: 1523
Crawling: http://info.cern.ch (depth=0)
  Document title: http://info.cern.ch - home of the first website
  Number of words: 487
...

Crawling completed. Total documents crawled: 15

Computing PageRank scores...
  Link graph size: 12 documents with outgoing links
  PageRank computed for 15 documents
  PageRank scores updated in database

============================================================
Crawl Statistics:
============================================================
Total words in lexicon:     3247
Total documents indexed:    15
Total inverted index entries: 8934
Total links in graph:       47
============================================================

Crawling completed successfully!
Database saved to: search_engine.db
```

### Step 4: Verify Database
```bash
# Check database was created
ls -lh search_engine.db

# Inspect database (optional)
sqlite3 search_engine.db "SELECT COUNT(*) FROM DocumentIndex;"
sqlite3 search_engine.db "SELECT url, page_rank FROM DocumentIndex ORDER BY page_rank DESC LIMIT 5;"
```

## Testing

The backend includes comprehensive unit tests in `test_crawler.py`:

### Test Categories

1. **PageRank Tests** (`TestPageRank`)
   - Simple 3-node graph
   - Linear chain graph
   - Isolated pages (no outgoing links)
   - Normalization

2. **Database Tests** (`TestSearchEngineDB`)
   - Insert words (with duplicates)
   - Insert documents (with duplicates)
   - Update document titles
   - Inverted index operations
   - Link graph operations
   - PageRank updates
   - Search with PageRank sorting
   - Database statistics

3. **Integration Tests** (`TestIntegration`)
   - Complete workflow (index → link → PageRank → search)
   - Verify search results sorted by PageRank

### Running Tests
```bash
python test_crawler.py
```

All tests should pass before submitting.

## Performance Considerations

### Memory vs. Disk
- **Lab 1**: All data in memory (fast but not persistent)
- **Lab 3**: All data in SQLite (persistent but slower)
- Database queries add 10-15ms overhead per search
- Trade-off is acceptable for persistence and scalability

### Optimization Tips
- Database indexes already created for common queries
- Crawler uses caching for word_id and doc_id lookups
- First link only counted (prevents duplicate links)
- Stop words filtered to reduce database size

## Troubleshooting

### Database Locked Error
```bash
# Close all connections to database
# Delete and regenerate if needed
rm search_engine.db
python crawler.py
```

### Crawling Timeout
```bash
# Some pages may timeout (3 second limit)
# This is normal and will be skipped
# Increase timeout if needed (edit crawler.py line 252)
```

### No Results After Crawling
```bash
# Check database has data
sqlite3 search_engine.db "SELECT COUNT(*) FROM DocumentIndex;"

# Verify PageRank was computed
sqlite3 search_engine.db "SELECT AVG(page_rank) FROM DocumentIndex;"
# Should be non-zero
```

### Import Errors
```bash
# Install dependencies
pip install -r requirements.txt
```

## Output Files

After running the backend, you will have:

1. **search_engine.db** - SQLite database containing:
   - All indexed words (Lexicon)
   - All crawled URLs (DocumentIndex)
   - Word-document mappings (InvertedIndex)
   - Page-to-page links (LinkGraph)
   - PageRank scores

2. This database file is ready for the frontend to use.

## AWS Deployment Notes

For AWS deployment (as per PDF section D2):

1. **Run crawler LOCALLY or on EECG machine** (not on AWS)
   ```bash
   python crawler.py urls.txt search_engine.db 1
   ```

2. **Copy database to AWS** (along with frontend files)
   ```bash
   scp -i your-key.pem search_engine.db ubuntu@YOUR_EC2_IP:~/
   scp -i your-key.pem frontend.py ubuntu@YOUR_EC2_IP:~/
   scp -i your-key.pem storage.py ubuntu@YOUR_EC2_IP:~/
   ```

3. **Do NOT copy crawler.py to AWS**
   - Database already contains all crawled data
   - Frontend reads directly from database
   - No need to re-crawl on AWS

## Summary

The backend successfully implements all Lab 3 requirements:

- ✓ Web crawler with persistent storage
- ✓ **Link extraction from anchor tags** (`<a href>`)
- ✓ PageRank algorithm implementation
- ✓ Complete database schema (Lexicon, DocumentIndex, InvertedIndex, LinkGraph)
- ✓ Reads from urls.txt
- ✓ Stores PageRank scores
- ✓ Unit tests for all components
- ✓ Ready for frontend integration

The generated `search_engine.db` file contains all indexed data and is ready to be used by the frontend for search queries.
