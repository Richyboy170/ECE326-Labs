# How to Run Benchmarks for Lab2 and Lab3

This guide provides step-by-step instructions for running performance benchmarks to compare Lab2 and Lab3.

## Prerequisites

### 1. Install Required Tools

```bash
# Install ApacheBench (for HTTP benchmarking)
sudo apt install apache2-utils -y

# Verify installation
ab -V
```

### 2. Ensure Dependencies are Installed

```bash
# Lab2 dependencies
cd Lab2
pip3 install -r requirements.txt
cd ..

# Lab3 dependencies
cd Lab3-test
pip3 install -r requirements.txt
cd ..
```

## Option 1: Automated Benchmarking (Recommended)

### Step 1: Make the script executable

```bash
chmod +x run_benchmarks.sh
```

### Step 2: Run Unit Test Benchmarks

These can run without servers running:

```bash
./run_benchmarks.sh
```

This will automatically:
- Run Lab2 unit tests and measure execution time
- Run Lab3 unit tests and measure execution time
- Save results to `benchmark_results/` directory

### Step 3: Run HTTP Benchmarks

You need to run these separately for Lab2 and Lab3 since they both use port 8080.

#### For Lab2:
```bash
# Terminal 1: Start Lab2 server
cd Lab2
python3 frontend.py

# Terminal 2: Run benchmarks (while server is running)
./run_benchmarks.sh

# Stop Lab2 server (Ctrl+C in Terminal 1)
```

#### For Lab3:
```bash
# Terminal 1: Generate database first (if not already done)
cd Lab3-test
python3 crawler.py

# Start Lab3 server
python3 frontend.py

# Terminal 2: Run benchmarks (while server is running)
./run_benchmarks.sh

# Stop Lab3 server (Ctrl+C in Terminal 1)
```

### Step 4: Analyze Results

```bash
python3 analyze_benchmarks.py
```

This will:
- Parse all benchmark results
- Generate a formatted summary
- Save summary to `benchmark_results/benchmark_summary.md`
- Display results in your terminal

## Option 2: Manual Benchmarking

### Part 1: Unit Test Benchmarks

#### Lab2 Unit Tests
```bash
cd Lab2
time python3 test_frontend.py
cd ..
```

Record the "real" time shown (e.g., `0m0.005s` = 0.005 seconds)

#### Lab3 Unit Tests
```bash
cd Lab3-test
time python3 test_crawler.py
cd ..
```

Record the "real" time shown (e.g., `0m0.944s` = 0.944 seconds)

### Part 2: HTTP Performance Benchmarks

#### Lab2 HTTP Benchmarks

```bash
# Terminal 1: Start server
cd Lab2
python3 frontend.py

# Terminal 2: Run benchmark
ab -n 1000 -c 10 http://localhost:8080/

# Record these metrics:
# - Time per request (mean)
# - Requests per second
```

#### Lab3 HTTP Benchmarks

```bash
# Terminal 1: Make sure database exists
cd Lab3-test
python3 crawler.py  # Only if search_engine.db doesn't exist

# Start server
python3 frontend.py

# Terminal 2: Run benchmarks
# Home page
ab -n 1000 -c 10 http://localhost:8080/

# Search functionality
ab -n 1000 -c 10 "http://localhost:8080/search?q=computer"

# Pagination
ab -n 1000 -c 10 "http://localhost:8080/search?q=computer&page=2"

# Record metrics for each test
```

## Understanding the Results

### ApacheBench Output - Key Metrics

When you run `ab`, look for these important lines:

```
Concurrency Level:      10
Time taken for tests:   2.145 seconds
Complete requests:      1000
Failed requests:        0
Requests per second:    466.20 [#/sec] (mean)
Time per request:       21.450 [ms] (mean)
```

**What to record:**
- **Time per request (mean)**: Average response time in milliseconds
- **Requests per second**: Throughput (how many requests per second)
- **Failed requests**: Should be 0

### Example Results

```markdown
## Benchmark Results

### Lab2 Performance
- Unit Test Execution: 0.005s
- Home Page Response: 12ms (mean), 833 req/s
- Concurrency Level: 10

### Lab3 Performance
- Unit Test Execution: 0.944s
- Home Page Response: 28ms (mean), 357 req/s
- Search Page Response: 38ms (mean), 263 req/s
- Pagination Response: 35ms (mean), 285 req/s
- Concurrency Level: 10

### Analysis Paragraph
[Copy from BENCHMARK_COMPARISON.md "One-Paragraph Summary" section]
```

## Adding Results to Your README

### For Lab3-test/README.md

Add a section like this:

```markdown
## Benchmark Results

[Paste the results from benchmark_summary.md here]

### Performance Analysis

[Paste the one-paragraph summary from BENCHMARK_COMPARISON.md here]
```

## Troubleshooting

### Server not starting

**Lab2:**
```bash
cd Lab2
python3 frontend.py
# If port 8080 is in use: pkill -f frontend.py
```

**Lab3:**
```bash
cd Lab3-test
# Make sure database exists
ls search_engine.db

# If not, generate it
python3 crawler.py

# Then start server
python3 frontend.py
```

### ApacheBench not installed

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install apache2-utils -y

# Check installation
ab -V
```

### Port 8080 already in use

```bash
# Find what's using port 8080
sudo lsof -i :8080

# Kill the process
pkill -f frontend.py

# Or kill by PID
kill <PID>
```

### Lab3 database not found

```bash
cd Lab3-test

# Check if database exists
ls -lh search_engine.db

# If not, generate it
python3 crawler.py urls.txt search_engine.db 1

# This will take a few minutes
```

### Unit tests failing

Make sure all dependencies are installed:

```bash
# Lab2
cd Lab2
pip3 install bottle beaker

# Lab3
cd Lab3-test
pip3 install beautifulsoup4 bottle urllib3
```

## Tips for Best Results

1. **Close other applications**: Minimize CPU usage from other programs
2. **Run multiple times**: Run benchmarks 2-3 times and average results
3. **Warm up the server**: Send 100 requests before benchmarking
4. **Same machine**: Run both Lab2 and Lab3 benchmarks on the same machine
5. **Document conditions**: Note machine specs, load, etc.

## Expected Performance Range

### Lab2 (OAuth Web App)
- Response time: 10-18ms
- Throughput: 800-1200 req/s
- Unit tests: < 0.01s

### Lab3 (Search Engine)
- Response time: 25-45ms
- Throughput: 250-400 req/s
- Unit tests: 0.5-1.5s

If your results are significantly different, check:
- Is the database properly indexed?
- Is the server under heavy load?
- Are there network issues?

## Questions?

Refer to:
- `BENCHMARK_COMPARISON.md` - Detailed comparison and analysis
- Lab3 PDF Section D3 - Requirements for benchmarking
- ApacheBench manual: `man ab`
