#!/usr/bin/env python3

import socket
import re
import sys
import ssl
import logging
import json
import time
import threading
from queue import Queue, Empty
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set, Optional
import requests
from bs4 import BeautifulSoup
import sqlite3

class AdvancedWebCrawler:
    """
    A sophisticated web crawler with advanced features for comprehensive web exploration.
    
    Key Features:
    - Multi-threaded crawling
    - Robust error handling
    - Persistent storage
    - Configurable crawling parameters
    - Intelligent link extraction
    - Performance monitoring
    """

    def __init__(self, 
                 base_url: str, 
                 max_depth: int = 3, 
                 max_pages: int = 100,
                 num_threads: int = 5):
        """
        Initialize the advanced web crawler.
        
        Args:
            base_url (str): Starting URL for crawling
            max_depth (int): Maximum crawl depth
            max_pages (int): Maximum number of pages to crawl
            num_threads (int): Number of concurrent crawling threads
        """
        # Logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Crawler configuration
        self.base_url = base_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.num_threads = num_threads

        # Thread-safe data structures
        self.visited_urls: Set[str] = set()
        self.url_queue: Queue = Queue()
        self.crawl_results: List[Dict] = []
        
        # Database connection for persistent storage
        self.init_database()

        # Performance tracking
        self.start_time = time.time()
        self.pages_crawled = 0
        self.errors_encountered = 0

    def init_database(self):
        """
        Initialize SQLite database for storing crawl results.
        """
        self.conn = sqlite3.connect('web_crawler_results.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Create tables for crawl results
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawl_results (
                url TEXT PRIMARY KEY,
                content TEXT,
                depth INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def is_valid_url(self, url: str) -> bool:
        """
        Validate and filter URLs.
        
        Args:
            url (str): URL to validate
        
        Returns:
            bool: Whether URL is valid and should be crawled
        """
        try:
            result = urlparse(url)
            return all([
                result.scheme in ['http', 'https'],
                result.netloc,
                not any(ext in url for ext in ['.pdf', '.jpg', '.png', '.gif'])
            ])
        except Exception as e:
            self.logger.warning(f"URL validation error: {e}")
            return False

    def extract_links(self, html_content: str, base_url: str) -> List[str]:
        """
        Extract and normalize links from HTML content.
        
        Args:
            html_content (str): HTML page content
            base_url (str): Base URL for link resolution
        
        Returns:
            List[str]: Extracted and normalized links
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = [
                urljoin(base_url, link.get('href'))
                for link in soup.find_all('a', href=True)
            ]
            return [
                link for link in links 
                if self.is_valid_url(link) and urlparse(link).netloc == urlparse(base_url).netloc
            ]
        except Exception as e:
            self.logger.error(f"Link extraction error: {e}")
            return []

    def safe_request(self, url: str, depth: int) -> Optional[str]:
        """
        Perform a safe HTTP request with error handling.
        
        Args:
            url (str): URL to request
            depth (int): Current crawl depth
        
        Returns:
            Optional[str]: Page content or None
        """
        try:
            response = requests.get(
                url, 
                timeout=10, 
                headers={'User-Agent': 'AdvancedWebCrawler/1.0'}
            )
            response.raise_for_status()
            
            # Store result in database
            self.cursor.execute(
                'INSERT OR REPLACE INTO crawl_results (url, content, depth) VALUES (?, ?, ?)',
                (url, response.text, depth)
            )
            self.conn.commit()
            
            return response.text
        
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            self.errors_encountered += 1
            return None

    def crawl_worker(self):
        """
        Worker thread for concurrent web crawling.
        """
        while True:
            try:
                url, depth = self.url_queue.get(timeout=5)
                
                if (
                    url in self.visited_urls or 
                    depth > self.max_depth or 
                    self.pages_crawled >= self.max_pages
                ):
                    continue
                
                self.visited_urls.add(url)
                page_content = self.safe_request(url, depth)
                
                if page_content:
                    self.pages_crawled += 1
                    links = self.extract_links(page_content, url)
                    
                    for link in links:
                        if link not in self.visited_urls:
                            self.url_queue.put((link, depth + 1))
                
            except Empty:
                break
            except Exception as e:
                self.logger.error(f"Crawling error: {e}")

    def start_crawl(self):
        """
        Initiate multi-threaded web crawling.
        """
        self.url_queue.put((self.base_url, 0))
        
        threads = [
            threading.Thread(target=self.crawl_worker)
            for _ in range(self.num_threads)
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()

    def generate_report(self):
        """
        Generate a comprehensive crawl report.
        
        Returns:
            Dict: Crawl statistics and summary
        """
        end_time = time.time()
        
        return {
            'base_url': self.base_url,
            'pages_crawled': self.pages_crawled,
            'max_depth_reached': self.max_depth,
            'total_time': round(end_time - self.start_time, 2),
            'errors_encountered': self.errors_encountered,
            'visited_urls': list(self.visited_urls)
        }

def main():
    if len(sys.argv) < 2:
        print("Usage: python web_crawler.py <base_url>")
        sys.exit(1)

    base_url = sys.argv[1]
    crawler = AdvancedWebCrawler(base_url)
    
    try:
        crawler.start_crawl()
        report = crawler.generate_report()
        print(json.dumps(report, indent=2))
    except Exception as e:
        print(f"Crawling failed: {e}")

if __name__ == "__main__":
    main()
