"""Tests for InvertedIndex class."""

import pytest
from inverted_index import InvertedIndex


def test_add_document():
    """Test adding documents to the index."""
    idx = InvertedIndex()
    idx.add_document("doc1", ["hello", "world"])

    assert "doc1" in idx.search("hello")
    assert "doc1" in idx.search("world")


def test_search_case_insensitive():
    """Test that search is case-insensitive."""
    idx = InvertedIndex()
    idx.add_document("doc1", ["Hello", "World"])

    assert "doc1" in idx.search("hello")
    assert "doc1" in idx.search("WORLD")


def test_search_nonexistent_term():
    """Test searching for a term that doesn't exist."""
    idx = InvertedIndex()
    idx.add_document("doc1", ["hello"])

    assert idx.search("goodbye") == set()


def test_multiple_documents():
    """Test with multiple documents."""
    idx = InvertedIndex()
    idx.add_document("doc1", ["hello", "world"])
    idx.add_document("doc2", ["hello", "python"])
    idx.add_document("doc3", ["world", "python"])

    assert idx.search("hello") == {"doc1", "doc2"}
    assert idx.search("world") == {"doc1", "doc3"}
    assert idx.search("python") == {"doc2", "doc3"}


def test_get_all_terms():
    """Test getting all terms in the index."""
    idx = InvertedIndex()
    idx.add_document("doc1", ["hello", "world"])
    idx.add_document("doc2", ["python"])

    terms = idx.get_all_terms()
    assert terms == ["hello", "python", "world"]


def test_get_document_count():
    """Test getting document count for a term."""
    idx = InvertedIndex()
    idx.add_document("doc1", ["hello"])
    idx.add_document("doc2", ["hello"])
    idx.add_document("doc3", ["world"])

    assert idx.get_document_count("hello") == 2
    assert idx.get_document_count("world") == 1
    assert idx.get_document_count("nonexistent") == 0


def test_empty_index():
    """Test operations on empty index."""
    idx = InvertedIndex()

    assert idx.search("anything") == set()
    assert idx.get_all_terms() == []
    assert idx.get_document_count("anything") == 0
