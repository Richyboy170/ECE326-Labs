"""
PageRank Algorithm Implementation

This module implements the PageRank algorithm for ranking web pages
based on their link structure. The algorithm iteratively computes
importance scores for each page based on incoming links.
"""


def page_rank(links, num_iterations=20, initial_pr=1.0):
    """
    Compute PageRank scores for a set of pages.

    Args:
        links: Dictionary mapping page_id -> list of page_ids it links to
               Example: {1: [2, 3], 2: [3], 3: [1]}
        num_iterations: Number of iterations to run the algorithm (default: 20)
        initial_pr: Initial PageRank value for each page (default: 1.0)

    Returns:
        Dictionary mapping page_id -> PageRank score

    Algorithm:
        PR(A) = (1-d) + d * sum(PR(Ti)/C(Ti))
        where:
        - d is damping factor (0.85)
        - Ti are pages that link to page A
        - C(Ti) is the number of outbound links from page Ti
    """
    damping = 0.85

    # Get all pages (both sources and targets)
    pages = set(links.keys())
    for targets in links.values():
        pages.update(targets)

    # Initialize PageRank scores
    page_rank_scores = {page: initial_pr for page in pages}

    # Build reverse link map (incoming links)
    inbound_links = {page: [] for page in pages}
    for source, targets in links.items():
        for target in targets:
            inbound_links[target].append(source)

    # Count outbound links for each page
    outbound_count = {}
    for page in pages:
        outbound_count[page] = len(links.get(page, []))
        # If a page has no outbound links, distribute its PR to all pages
        if outbound_count[page] == 0:
            outbound_count[page] = len(pages)

    # Iterate to compute PageRank
    for iteration in range(num_iterations):
        new_page_rank = {}

        for page in pages:
            # Start with the damping factor component
            rank = (1 - damping)

            # Add contributions from pages that link to this page
            for linking_page in inbound_links[page]:
                rank += damping * (page_rank_scores[linking_page] / outbound_count[linking_page])

            # Handle pages with no outbound links (distribute to all pages)
            for linking_page in pages:
                if outbound_count[linking_page] == len(pages) and linking_page != page:
                    rank += damping * (page_rank_scores[linking_page] / len(pages))

            new_page_rank[page] = rank

        page_rank_scores = new_page_rank

    return page_rank_scores


def normalize_page_rank(page_rank_scores):
    """
    Normalize PageRank scores so they sum to 1.0

    Args:
        page_rank_scores: Dictionary mapping page_id -> PageRank score

    Returns:
        Dictionary with normalized PageRank scores
    """
    total = sum(page_rank_scores.values())
    if total == 0:
        return page_rank_scores

    return {page: score / total for page, score in page_rank_scores.items()}


if __name__ == "__main__":
    # Test the PageRank algorithm with a simple example
    print("Testing PageRank Algorithm\n")

    # Example link graph:
    # Page 1 -> Page 2, 3
    # Page 2 -> Page 3
    # Page 3 -> Page 1
    test_links = {
        1: [2, 3],
        2: [3],
        3: [1]
    }

    print("Link structure:")
    for source, targets in test_links.items():
        print(f"  Page {source} links to: {targets}")

    scores = page_rank(test_links)
    normalized_scores = normalize_page_rank(scores)

    print("\nPageRank scores:")
    for page in sorted(scores.keys()):
        print(f"  Page {page}: {scores[page]:.4f} (normalized: {normalized_scores[page]:.4f})")
