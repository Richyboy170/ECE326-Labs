#!/usr/bin/env python
"""
Populate the database with demo data for testing the search engine
"""

from storage import SearchEngineDB
from pagerank import page_rank, normalize_page_rank

def populate_demo_database():
    """Create a demo database with sample data"""

    print("Creating demo database...")

    # Create database
    db = SearchEngineDB('search_engine.db')

    # Sample documents
    documents = [
        {
            'url': 'http://example.com/python-tutorial',
            'title': 'Python Programming Tutorial',
            'words': [
                ('python', 7), ('programming', 5), ('tutorial', 5),
                ('learn', 3), ('code', 3), ('beginner', 3),
                ('advanced', 2), ('syntax', 2), ('examples', 2)
            ]
        },
        {
            'url': 'http://example.com/data-science',
            'title': 'Data Science with Python',
            'words': [
                ('data', 7), ('science', 7), ('python', 5),
                ('analysis', 4), ('pandas', 3), ('numpy', 3),
                ('matplotlib', 2), ('visualization', 2)
            ]
        },
        {
            'url': 'http://example.com/machine-learning',
            'title': 'Machine Learning Guide',
            'words': [
                ('machine', 7), ('learning', 7), ('python', 5),
                ('algorithm', 4), ('model', 4), ('training', 3),
                ('neural', 2), ('network', 2), ('tensorflow', 2)
            ]
        },
        {
            'url': 'http://example.com/web-development',
            'title': 'Web Development with Python',
            'words': [
                ('web', 7), ('development', 7), ('python', 5),
                ('flask', 4), ('django', 4), ('server', 3),
                ('api', 3), ('database', 3)
            ]
        },
        {
            'url': 'http://example.com/python-basics',
            'title': 'Python Basics for Beginners',
            'words': [
                ('python', 7), ('basics', 7), ('beginner', 5),
                ('variables', 4), ('functions', 4), ('loops', 3),
                ('conditions', 3), ('syntax', 3)
            ]
        }
    ]

    # Insert documents and words
    doc_ids = {}
    for doc in documents:
        doc_id = db.insert_document(doc['url'], doc['title'])
        doc_ids[doc['url']] = doc_id

        # Insert words into inverted index
        for word, font_size in doc['words']:
            word_id = db.insert_word(word)
            db.insert_inverted_index(word_id, doc_id, font_size)

    print(f"Inserted {len(documents)} documents")

    # Create link graph
    # Python tutorial is linked to by most pages (high PageRank)
    # Data science links to ML and web dev
    # Web dev links to basics
    links = {
        doc_ids['http://example.com/data-science']: [
            doc_ids['http://example.com/python-tutorial'],
            doc_ids['http://example.com/machine-learning'],
            doc_ids['http://example.com/web-development']
        ],
        doc_ids['http://example.com/machine-learning']: [
            doc_ids['http://example.com/python-tutorial'],
            doc_ids['http://example.com/data-science']
        ],
        doc_ids['http://example.com/web-development']: [
            doc_ids['http://example.com/python-tutorial'],
            doc_ids['http://example.com/python-basics']
        ],
        doc_ids['http://example.com/python-basics']: [
            doc_ids['http://example.com/python-tutorial']
        ]
    }

    # Insert links
    total_links = 0
    for from_id, to_ids in links.items():
        for to_id in to_ids:
            db.insert_link(from_id, to_id)
            total_links += 1

    print(f"Inserted {total_links} links")

    # Compute PageRank
    link_graph = db.get_link_graph()
    page_ranks = page_rank(link_graph, num_iterations=20)
    page_ranks = normalize_page_rank(page_ranks)

    # Update database
    db.update_page_ranks(page_ranks)

    print("\nPageRank scores:")
    for url, doc_id in sorted(doc_ids.items(), key=lambda x: page_ranks.get(x[1], 0), reverse=True):
        score = page_ranks.get(doc_id, 0)
        print(f"  {url}: {score:.6f}")

    # Print statistics
    stats = db.get_statistics()
    print("\nDatabase statistics:")
    print(f"  Total words: {stats['total_words']}")
    print(f"  Total documents: {stats['total_documents']}")
    print(f"  Total inverted index entries: {stats['total_index_entries']}")
    print(f"  Total links: {stats['total_links']}")

    # Test search
    print("\nTest search for 'python':")
    results = db.search_word('python', limit=5)
    for i, (url, title, rank) in enumerate(results, 1):
        print(f"  {i}. {title} (PageRank: {rank:.6f})")
        print(f"     {url}")

    db.close()
    print("\nDemo database created successfully!")

if __name__ == "__main__":
    populate_demo_database()
