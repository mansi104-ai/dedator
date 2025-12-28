#!/usr/bin/env python3

import sys
import json
from web_scraper import WebScraper

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_scraper.py <url> [depth]")
        print("Example: python scripts/run_scraper.py https://example.com 1")
        sys.exit(1)
    
    url = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    print(f"Scraping {url} with depth {depth}...")
    scraper = WebScraper(max_pages=10)
    result = scraper.crawl(url, depth)
    
    print(json.dumps(result, indent=2))
