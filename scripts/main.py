import json
import sys
import os


try:
    # When called from parent directory
    from separation import run_analytics_pipeline
    from web_scraper import WebScraper
except ImportError:
    # When called as a module
    from scripts.separation import run_analytics_pipeline
    from scripts.web_scraper import WebScraper

def main():
    """
    Main entry point for the analytics processor.
    Expects raw JSON via stdin or file.
    """
    try:
        # Read input from stdin
        raw_input = sys.stdin.read()
        
        data = json.loads(raw_input) if raw_input else {}
        
        url = data.get('url')
        if url:
            scraper = WebScraper(max_pages=5)
            scrape_result = scraper.crawl(url, depth=data.get('depth', 0))
            
            if scrape_result.get('success'):
                # Combine scrape data with analytics
                print(json.dumps({
                    "type": "scrape_analytics",
                    "data": scrape_result
                }))
                return
            else:
                print(json.dumps({"error": "Scraping failed", "details": scrape_result.get('error')}))
                return

        # Fallback to existing analytics pipeline
        results = run_analytics_pipeline()
        print(json.dumps(results))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
