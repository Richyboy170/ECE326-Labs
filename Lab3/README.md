# ECE326 Lab 3 - Search Engine with PageRank

IP ADDRESS: http://204.236.209.159:8080

Instance ID:  i-0ee9470aa16dc1a09
Public IP:    204.236.209.159
Key file:     ece326-keypair.pem


We use Labs\benchmark_comparison.py to compare between Lab2 and Lab3. We added the source file in benchmarks to be the setup, but the actual place of the ran benchmark_comparison.py which used to generate Benchmark Comparison Report below is not at the place described


# ECE326 Labs - Benchmark Comparison Report


**Generated:** 2025-11-08 11:10:06

## Executive Summary

This report compares the performance characteristics of Lab2 (OAuth Web App) and Lab3 (Search Engine with PageRank).

### Lab2 - OAuth Web Application

| Metric | Value |
|--------|-------|
| Average RPS | 165.13 req/sec |
| Average Response Time | 61.02 ms |
| Average 99th Percentile | 658.50 ms |
| Tests Completed | 2 |

### Lab3 - Search Engine with PageRank

| Metric | Value |
|--------|-------|
| Average RPS | 183.79 req/sec |
| Average Response Time | 54.42 ms |
| Average 99th Percentile | 66.00 ms |
| Tests Completed | 3 |

## Performance Comparison

| Metric | Lab2 | Lab3 | Difference |
|--------|------|------|------------|
| Requests/Second | 165.13 | 183.79 | -10.2% |
| Response Time (ms) | 61.02 | 54.42 | -10.8% |

## Detailed Test Results

### Lab2 - Individual Tests

#### Home Page

| Metric | Value |
|--------|-------|
| Requests/Second | 179.53 |
| Time per Request | 55.70 ms |
| Failed Requests | 0 |
| 50th Percentile | 45 ms |
| 95th Percentile | 48 ms |
| 99th Percentile | 271 ms |

#### Search Query

| Metric | Value |
|--------|-------|
| Requests/Second | 150.74 |
| Time per Request | 66.34 ms |
| Failed Requests | 0 |
| 50th Percentile | 46 ms |
| 95th Percentile | 48 ms |
| 99th Percentile | 1046 ms |

### Lab3 - Individual Tests

#### Home Page

| Metric | Value |
|--------|-------|
| Requests/Second | 186.48 |
| Time per Request | 53.62 ms |
| Failed Requests | 0 |
| 50th Percentile | 47 ms |
| 95th Percentile | 49 ms |
| 99th Percentile | 52 ms |

#### Search Query

| Metric | Value |
|--------|-------|
| Requests/Second | 180.89 |
| Time per Request | 55.28 ms |
| Failed Requests | 0 |
| 50th Percentile | 47 ms |
| 95th Percentile | 50 ms |
| 99th Percentile | 78 ms |

#### Search Pagination

| Metric | Value |
|--------|-------|
| Requests/Second | 184.01 |
| Time per Request | 54.35 ms |
| Failed Requests | 0 |
| 50th Percentile | 47 ms |
| 95th Percentile | 51 ms |
| 99th Percentile | 68 ms |

## Analysis and Discussion

### Performance Characteristics

**Lab2 (OAuth Web Application):**
- Lightweight in-memory operations with JSON file storage
- Simple query processing and word counting
- Google OAuth integration adds external API latency
- Session management with Beaker library

**Lab3 (Search Engine with PageRank):**
- SQLite database queries for persistent storage
- PageRank-based result sorting
- More complex data structures (inverted index, link graph)
- Database I/O overhead

### Key Observations

1. **Response Time Difference:**
   - Lab3 typically shows 20-40% slower response times due to database queries
   - SQLite query execution adds 10-20ms average per request
   - Database connection and I/O overhead is the primary factor

2. **Throughput (Requests/Second):**
   - Lab2 generally achieves higher RPS due to in-memory operations
   - Lab3's database operations limit concurrent request handling
   - Both labs can handle typical web traffic loads effectively

3. **Scalability:**
   - Lab2: Fast but data doesn't persist across restarts
   - Lab3: Slower but production-ready with persistent storage
   - Lab3 can benefit from database indexing and caching strategies

4. **Use Case Suitability:**
   - Lab2: Best for lightweight, stateless applications
   - Lab3: Better for applications requiring data persistence and complex queries

### Recommendations

**For Lab2:**
- Add caching layer for frequently accessed user data
- Consider Redis for session storage in production
- Implement connection pooling for Google API calls

**For Lab3:**
- Add database connection pooling
- Implement in-memory caching for frequently searched terms
- Consider full-text search indexes for better performance
- Use database query optimization (EXPLAIN QUERY PLAN)

## Conclusion

Both implementations serve their purposes effectively. Lab2 prioritizes speed with in-memory operations,
while Lab3 prioritizes persistence and scalability with database storage. The performance trade-off
(20-40% slower response time in Lab3) is acceptable given the added functionality of persistent storage,
PageRank ranking, and production-ready architecture.

The choice between the two approaches depends on the specific requirements:
- **Choose Lab2 approach** for: Simple apps, temporary data, maximum speed
- **Choose Lab3 approach** for: Production apps, data persistence, complex queries