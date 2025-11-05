# Benchmark Comparison: Lab2 vs Lab3

## Overview

This document compares the benchmark tests for Lab2 and Lab3 in terms of structure, coverage, and comprehensiveness.

## Test Statistics

| Metric | Lab2 | Lab3 |
|--------|------|------|
| **Total Tests** | 28 | 13 |
| **Test Classes** | 8 | 3 |
| **Application Type** | OAuth Web App | Search Engine |
| **Storage Type** | JSON Files | SQLite Database |
| **Execution Time** | ~0.005s | ~0.944s |

## Test Structure Comparison

### Lab2 Test Classes
1. `TestWordCounting` (5 tests) - Core counting logic
2. `TestQueryProcessing` (4 tests) - Input processing
3. `TestUserDataStructure` (2 tests) - Data model
4. `TestRecentWordsTracking` (5 tests) - LIFO queue logic
5. `TestJSONPersistence` (3 tests) - File storage
6. `TestIntegrationWorkflow` (2 tests) - End-to-end
7. `TestEdgeCases` (5 tests) - Edge cases
8. `TestWordCountTable` (2 tests) - Output validation

### Lab3 Test Classes
1. `TestPageRank` (4 tests) - Algorithm testing
2. `TestSearchEngineDB` (8 tests) - Database operations
3. `TestIntegration` (1 test) - Complete workflow

## Coverage Analysis

### Lab2 Coverage
- ✓ Unit tests for each core function
- ✓ Edge case testing (empty, unicode, special chars)
- ✓ Data structure validation
- ✓ Persistence layer testing
- ✓ Integration workflows
- ✗ No performance/benchmark tests
- ✗ No authentication testing (OAuth mocked)
- ✗ No HTTP endpoint testing

### Lab3 Coverage
- ✓ Algorithm correctness (PageRank)
- ✓ Database CRUD operations
- ✓ Data integrity testing
- ✓ Multi-entity relationships (links, documents, words)
- ✓ Integration workflow
- ✗ No crawler unit tests
- ✗ No edge case testing
- ✗ No performance benchmarks

## Strengths & Weaknesses

### Lab2 Benchmark Strengths
- **More granular**: 28 tests vs 13 tests
- **Better edge case coverage**: Tests empty inputs, unicode, special characters
- **Focused unit testing**: Each function tested independently
- **Fast execution**: Completes in ~5ms

### Lab2 Benchmark Weaknesses
- **No web framework testing**: Bottle routes not tested
- **No session management tests**: Beaker sessions not validated
- **Limited integration tests**: Only 2 integration tests

### Lab3 Benchmark Strengths
- **Algorithm verification**: PageRank implementation validated
- **Database integrity**: Comprehensive DB operation testing
- **Complex integration**: Tests complete indexing workflow
- **Real-world simulation**: Uses actual database operations

### Lab3 Benchmark Weaknesses
- **Fewer edge cases**: Doesn't test edge cases extensively
- **No crawler tests**: Main crawler.py not unit tested
- **Missing frontend tests**: No frontend.py testing
- **Lower test count**: 13 tests vs Lab2's 28

## Comparability

### What CAN Be Compared
1. **Test structure and organization** - Both use unittest framework
2. **Code coverage percentage** - Can measure % of code tested
3. **Test execution time** - Performance of test suite
4. **Integration test depth** - Complexity of workflows tested
5. **Documentation quality** - Both have descriptive docstrings

### What CANNOT Be Directly Compared
1. **Feature parity** - Different applications with different features
2. **Absolute test count** - Lab2 has simpler functions requiring more unit tests
3. **Test complexity** - Lab3 tests are more complex (DB, algorithms)
4. **Domain logic** - OAuth/word tracking vs search engine/PageRank

## Recommendations

### To Make Lab2 More Comprehensive
1. Add HTTP endpoint tests using Bottle test client
2. Add session management tests (mock Beaker)
3. Add authentication flow tests (mock OAuth)
4. Add performance benchmarks for query processing
5. Add concurrent user tests

### To Make Lab3 More Comprehensive
1. Add unit tests for crawler.py functions
2. Add edge case tests (empty DB, invalid URLs)
3. Add frontend.py route tests
4. Add performance benchmarks for PageRank
5. Add tests for large-scale data (1000+ documents)
6. Add crawler timeout and error handling tests

## Test Quality Metrics

| Metric | Lab2 | Lab3 |
|--------|------|------|
| **Tests per Function** | ~3-4 | ~2-3 |
| **Edge Cases Tested** | High | Low |
| **Integration Depth** | Medium | High |
| **Execution Speed** | Excellent | Good |
| **Documentation** | Excellent | Good |
| **Maintainability** | High | High |

## Conclusion

**Lab2** has a more comprehensive unit test suite with better edge case coverage but lacks integration testing for the web framework.

**Lab3** has stronger integration tests and validates complex algorithms but could benefit from more granular unit tests and edge case coverage.

Both benchmarks are well-structured and serve their purposes effectively. They complement each other by demonstrating different testing approaches:
- Lab2: Bottom-up (unit tests → integration)
- Lab3: Top-down (integration → unit tests)

To achieve parity, Lab3 should add ~15 more tests covering edge cases and crawler functionality.
