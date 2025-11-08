"""
Web Crawler with PageRank and Persistent Storage

This crawler extends the Lab 1 crawler by adding:
- Persistent storage using SQLite database
- PageRank computation for ranking search results
- Link graph construction for PageRank algorithm
"""

import urllib3
from urllib.parse import urlparse, urldefrag, urljoin
from urllib.request import urlopen
from bs4 import BeautifulSoup, Tag
from collections import defaultdict
import re

from storage import SearchEngineDB
from pagerank import page_rank, normalize_page_rank

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""


WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')


class Crawler(object):
    """Web crawler with persistent storage and PageRank support"""

    def __init__(self, db_file, url_file):
        """
        Initialize the crawler

        Args:
            db_file: Path to SQLite database file
            url_file: Path to file containing seed URLs
        """
        self.db = SearchEngineDB(db_file)
        self._url_queue = []
        self._doc_id_cache = {}
        self._word_id_cache = {}
        self._link_cache = set()  # Track links already added to avoid duplicates

        # Functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # Add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # Record the currently indexed document's title and increase font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # Increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # Decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # Never go in and parse these tags
        self._ignored_tags = {
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame',
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset',
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param'
        }

        # Set of words to ignore
        self._ignored_words = {
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it', 'a', 'b', 'c', 'd',
            'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
            'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or'
        }

        # Keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # Get all URLs into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            print(f"Warning: Could not open {url_file}")

    def word_id(self, word):
        """Get the word id of some specific word"""
        if word in self._word_id_cache:
            return self._word_id_cache[word]

        word_id = self.db.insert_word(word)
        self._word_id_cache[word] = word_id
        return word_id

    def document_id(self, url):
        """Get the document id for some url"""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]

        doc_id = self.db.insert_document(url)
        self._doc_id_cache[url] = doc_id
        return doc_id

    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url"""
        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""

        # Compute the new url based on import
        curr_url = urldefrag(curr_url)[0]
        parsed_url = urlparse(curr_url)
        return urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database"""
        # Only count the first link between two documents
        link_key = (from_doc_id, to_doc_id)
        if link_key not in self._link_cache:
            self.db.insert_link(from_doc_id, to_doc_id)
            self._link_cache.add(link_key)

    def _visit_title(self, elem):
        """Called when visiting the <title> tag"""
        title_text = self._text_of(elem).strip()
        print(f"  Document title: {title_text[:60]}...")
        self.db.update_document_title(self._curr_doc_id, title_text)

    def _visit_a(self, elem):
        """Called when visiting <a> tags"""
        dest_url = self._fix_url(self._curr_url, attr(elem, "href"))

        # Add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))

        # Add a link entry into the database
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

    def _add_words_to_document(self):
        """Add all words in self._curr_words to the database for current document"""
        print(f"  Number of words: {len(self._curr_words)}")

        for word_id, font_size in self._curr_words:
            self.db.insert_inverted_index(word_id, self._curr_doc_id, font_size)

    def _increase_font_factor(self, factor):
        """Increase/decrease the current font size"""
        def increase_it(elem):
            self._font_size += factor
        return increase_it

    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document"""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._curr_words.append((self.word_id(word), self._font_size))

    def _text_of(self, elem):
        """Get the text inside some element without any tags"""
        if isinstance(elem, Tag):
            text = []
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when
        entering and leaving tags"""

        class DummyTag(object):
            next = False
            name = ''

        class NextTag(object):
            def __init__(self, obj):
                self.next = obj

        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # HTML tag
            if isinstance(tag, Tag):
                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # Ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    continue

                # Enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # Text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        seen = set()

        print(f"\nStarting crawl with depth={depth}, timeout={timeout}s")
        print(f"Initial URL queue size: {len(self._url_queue)}\n")

        while len(self._url_queue):
            url, depth_ = self._url_queue.pop()

            # Skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # We've already seen this document
            if doc_id in seen:
                continue

            seen.add(doc_id)

            socket = None
            try:
                print(f"Crawling: {url} (depth={depth_})")
                socket = urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read(), features="html.parser")

                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = []
                self._index_document(soup)
                self._add_words_to_document()

            except Exception as e:
                print(f"  Error: {e}")
            finally:
                if socket:
                    socket.close()

        print(f"\nCrawling completed. Total documents crawled: {len(seen)}")

    def compute_page_rank(self, num_iterations=20):
        """Compute PageRank scores for all documents"""
        print("\nComputing PageRank scores...")

        # Get the link graph from database
        link_graph = self.db.get_link_graph()
        print(f"  Link graph size: {len(link_graph)} documents with outgoing links")

        # Compute PageRank
        page_ranks = page_rank(link_graph, num_iterations=num_iterations)
        print(f"  PageRank computed for {len(page_ranks)} documents")

        # Normalize scores
        page_ranks = normalize_page_rank(page_ranks)

        # Update database with PageRank scores
        self.db.update_page_ranks(page_ranks)
        print("  PageRank scores updated in database")

        return page_ranks

    def print_statistics(self):
        """Print statistics about the crawled data"""
        stats = self.db.get_statistics()
        print("\n" + "=" * 60)
        print("Crawl Statistics:")
        print("=" * 60)
        print(f"Total words in lexicon:     {stats['total_words']}")
        print(f"Total documents indexed:    {stats['total_documents']}")
        print(f"Total inverted index entries: {stats['total_index_entries']}")
        print(f"Total links in graph:       {stats['total_links']}")
        print("=" * 60)

    def close(self):
        """Close the database connection"""
        self.db.close()


if __name__ == "__main__":
    import sys

    # Default parameters
    url_file = "urls.txt"
    db_file = "search_engine.db"
    depth = 1
    timeout = 3

    # Parse command line arguments
    if len(sys.argv) > 1:
        url_file = sys.argv[1]
    if len(sys.argv) > 2:
        db_file = sys.argv[2]
    if len(sys.argv) > 3:
        depth = int(sys.argv[3])

    print("=" * 60)
    print("ECE326 Lab 3 - Web Crawler with PageRank")
    print("=" * 60)
    print(f"URL file: {url_file}")
    print(f"Database: {db_file}")
    print(f"Crawl depth: {depth}")
    print("=" * 60)

    # Create and run crawler
    crawler = Crawler(db_file, url_file)

    try:
        # Crawl the web
        crawler.crawl(depth=depth, timeout=timeout)

        # Compute PageRank
        crawler.compute_page_rank()

        # Print statistics
        crawler.print_statistics()

    finally:
        crawler.close()

    print("\nCrawling completed successfully!")
    print(f"Database saved to: {db_file}")
