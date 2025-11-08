#!/bin/bash
# ECE326 Labs Benchmark Script
# This script runs performance benchmarks for Lab2 and Lab3

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ECE326 Labs Benchmark Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create results directory
RESULTS_DIR="benchmark_results"
mkdir -p "$RESULTS_DIR"

# Get timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${GREEN}Part 1: Unit Test Benchmarks${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Lab2 Unit Tests
echo -e "${YELLOW}Running Lab2 unit tests...${NC}"
cd Lab2
if [ -f "test_frontend.py" ]; then
    echo "Time taken:" > "../$RESULTS_DIR/lab2_unittest_${TIMESTAMP}.txt"
    (time python3 test_frontend.py 2>&1) >> "../$RESULTS_DIR/lab2_unittest_${TIMESTAMP}.txt"
    echo -e "${GREEN}✓ Lab2 unit tests completed${NC}"
    echo "Results saved to: $RESULTS_DIR/lab2_unittest_${TIMESTAMP}.txt"
else
    echo -e "${RED}✗ test_frontend.py not found${NC}"
fi
cd ..
echo ""

# Lab3 Unit Tests
echo -e "${YELLOW}Running Lab3 unit tests...${NC}"
cd Lab3-test
if [ -f "test_crawler.py" ]; then
    echo "Time taken:" > "../$RESULTS_DIR/lab3_unittest_${TIMESTAMP}.txt"
    (time python3 test_crawler.py 2>&1) >> "../$RESULTS_DIR/lab3_unittest_${TIMESTAMP}.txt"
    echo -e "${GREEN}✓ Lab3 unit tests completed${NC}"
    echo "Results saved to: $RESULTS_DIR/lab3_unittest_${TIMESTAMP}.txt"
else
    echo -e "${RED}✗ test_crawler.py not found${NC}"
fi
cd ..
echo ""

echo -e "${GREEN}Part 2: HTTP Performance Benchmarks${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if ApacheBench is installed
if ! command -v ab &> /dev/null; then
    echo -e "${YELLOW}ApacheBench (ab) not found. Installing...${NC}"
    echo "Run: sudo apt install apache2-utils -y"
    echo -e "${RED}Please install ApacheBench and re-run this script${NC}"
    exit 1
fi

# Check if servers are running
echo -e "${YELLOW}Checking if Lab2 server is running on port 8080...${NC}"
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Lab2 server detected on port 8080${NC}"

    echo -e "${YELLOW}Running Lab2 HTTP benchmarks...${NC}"
    ab -n 1000 -c 10 http://localhost:8080/ > "$RESULTS_DIR/lab2_homepage_${TIMESTAMP}.txt" 2>&1
    echo -e "${GREEN}✓ Lab2 HTTP benchmark completed${NC}"
    echo "Results saved to: $RESULTS_DIR/lab2_homepage_${TIMESTAMP}.txt"
    echo ""
else
    echo -e "${RED}✗ Lab2 server not running on port 8080${NC}"
    echo "To start Lab2 server: cd Lab2 && python3 frontend.py"
    echo ""
fi

echo -e "${YELLOW}Checking if Lab3 server is running on port 8080...${NC}"
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Lab3 server detected on port 8080${NC}"

    echo -e "${YELLOW}Running Lab3 HTTP benchmarks...${NC}"

    # Home page
    ab -n 1000 -c 10 http://localhost:8080/ > "$RESULTS_DIR/lab3_homepage_${TIMESTAMP}.txt" 2>&1
    echo -e "${GREEN}✓ Lab3 home page benchmark completed${NC}"

    # Search functionality
    ab -n 1000 -c 10 "http://localhost:8080/search?q=computer" > "$RESULTS_DIR/lab3_search_${TIMESTAMP}.txt" 2>&1
    echo -e "${GREEN}✓ Lab3 search benchmark completed${NC}"

    # Pagination
    ab -n 1000 -c 10 "http://localhost:8080/search?q=computer&page=2" > "$RESULTS_DIR/lab3_pagination_${TIMESTAMP}.txt" 2>&1
    echo -e "${GREEN}✓ Lab3 pagination benchmark completed${NC}"

    echo "Results saved to:"
    echo "  - $RESULTS_DIR/lab3_homepage_${TIMESTAMP}.txt"
    echo "  - $RESULTS_DIR/lab3_search_${TIMESTAMP}.txt"
    echo "  - $RESULTS_DIR/lab3_pagination_${TIMESTAMP}.txt"
    echo ""
else
    echo -e "${RED}✗ Lab3 server not running on port 8080${NC}"
    echo "To start Lab3 server: cd Lab3-test && python3 frontend.py"
    echo ""
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Benchmark Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo "All results saved to: $RESULTS_DIR/"
echo ""
echo "To view results:"
echo "  - Lab2 unit tests: cat $RESULTS_DIR/lab2_unittest_${TIMESTAMP}.txt"
echo "  - Lab3 unit tests: cat $RESULTS_DIR/lab3_unittest_${TIMESTAMP}.txt"
echo "  - Lab2 HTTP: cat $RESULTS_DIR/lab2_homepage_${TIMESTAMP}.txt"
echo "  - Lab3 HTTP: cat $RESULTS_DIR/lab3_*_${TIMESTAMP}.txt"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Review the benchmark results"
echo "2. Extract key metrics (response time, req/s)"
echo "3. Add results to your README.md"
echo "4. Include the one-paragraph analysis from BENCHMARK_COMPARISON.md"
