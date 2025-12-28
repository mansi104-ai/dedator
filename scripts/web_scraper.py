import sys
import json
import re
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Any
import time

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class WebScraper:
    def __init__(self, timeout: int = 10, max_pages: int = 10):
        self.timeout = timeout
        self.max_pages = max_pages
        self.session = self._create_session()
        self.visited_urls: Set[str] = set()
        
    def _create_session(self) -> requests.Session:
        """Create session with retry strategy and proper headers."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        return session
    
    def detect_technologies(self, soup: BeautifulSoup, headers: Dict, html: str) -> List[str]:
        tech = []
        
        # Check meta tags
        meta_generator = soup.find('meta', attrs={'name': 'generator'})
        if meta_generator and meta_generator.get('content'):
            tech.append(meta_generator['content'])
        
        # Check for frameworks in HTML
        if '_next' in html or 'next.js' in html.lower():
            tech.append('Next.js')
        if 'react' in html.lower() or soup.find(attrs={'data-reactroot': True}):
            tech.append('React')
        if 'wp-content' in html or 'wordpress' in html.lower():
            tech.append('WordPress')
        if 'vue' in html.lower() or soup.find(attrs={'data-v-': re.compile('.*')}):
            tech.append('Vue.js')
        if 'angular' in html.lower() or soup.find(attrs={'ng-': re.compile('.*')}):
            tech.append('Angular')
        
        # Check for CSS frameworks
        if 'tailwind' in html.lower() or 'tw-' in html:
            tech.append('Tailwind CSS')
        if 'bootstrap' in html.lower():
            tech.append('Bootstrap')
        
        # Check headers
        server = headers.get('server', '').lower()
        if server:
            tech.append(f"Server: {server}")
        
        powered_by = headers.get('x-powered-by', '')
        if powered_by:
            tech.append(f"Powered by: {powered_by}")
        
        return list(set(tech))  # Remove duplicates
    
    def extract_data(self, url: str, soup: BeautifulSoup, headers: Dict, html: str) -> Dict[str, Any]:
        base_domain = urlparse(url).netloc
        
        # Title
        title = soup.title.string.strip() if soup.title else ""
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '').strip() if meta_desc else ""
        
        # Headings
        headings = []
        for level in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            for heading in soup.find_all(level):
                text = heading.get_text(strip=True)
                if text:
                    headings.append(text)
        
        # Links (internal and external)
        links = []
        internal_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)
            
            # Skip anchors, mailto, tel, javascript
            if absolute_url.startswith(('#', 'mailto:', 'tel:', 'javascript:')):
                continue
                
            links.append(absolute_url)
            
            # Check if internal
            if urlparse(absolute_url).netloc == base_domain:
                internal_links.append(absolute_url)
        
        # Remove duplicates
        links = list(set(links))
        
        # Images
        images = []
        for img in soup.find_all('img'):
            img_data = {
                'url': urljoin(url, img.get('src', '')),
                'alt': img.get('alt', '')
            }
            if img_data['url']:
                images.append(img_data)
        
        # Main content (remove scripts, styles, nav, footer, etc.)
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        text_content = soup.get_text(separator=' ', strip=True)
        # Clean whitespace
        text_content = re.sub(r'\s+', ' ', text_content)
        content_summary = text_content[:500]
        
        # Technology detection
        detected_tech = self.detect_technologies(soup, headers, html)
        
        return {
            'title': title,
            'description': description,
            'headings': headings,
            'links': links,
            'internal_links': internal_links,
            'images': images,
            'content_summary': content_summary,
            'detected_tech': detected_tech
        }
    
    def scrape_url(self, url: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            response_time_ms = int((time.time() - start_time) * 1000)
            
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract data
            extracted_data = self.extract_data(url, soup, response.headers, response.text)
            
            return {
                'success': True,
                'url': url,
                'extracted_data': extracted_data,
                'metadata': {
                    'status_code': response.status_code,
                    'response_time_ms': response_time_ms,
                    'content_type': response.headers.get('content-type', ''),
                    'content_size_bytes': len(response.content),
                    'scraped_at': datetime.now(timezone.utc).isoformat(),
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'error_type': 'unexpected_error'
            }
    
    def crawl(self, start_url: str, depth: int) -> Dict[str, Any]:
        results = []
        to_visit = [(start_url, 0)]  # (url, current_depth)
        
        while to_visit and len(results) < self.max_pages:
            url, current_depth = to_visit.pop(0)
            
            # Skip if already visited
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            # Scrape the page
            result = self.scrape_url(url)
            results.append(result)
            
            # If depth allows and scrape was successful, add internal links
            if current_depth < depth and result['success']:
                internal_links = result['extracted_data'].get('internal_links', [])
                for link in internal_links:
                    if link not in self.visited_urls and len(results) + len(to_visit) < self.max_pages:
                        to_visit.append((link, current_depth + 1))
        
        # Aggregate results
        if results:
            main_result = results[0]
            
            # Combine data from all pages if depth > 0
            if len(results) > 1:
                all_links = []
                all_images = []
                all_headings = []
                all_tech = []
                
                for r in results:
                    if r['success']:
                        all_links.extend(r['extracted_data'].get('links', []))
                        all_images.extend(r['extracted_data'].get('images', []))
                        all_headings.extend(r['extracted_data'].get('headings', []))
                        all_tech.extend(r['extracted_data'].get('detected_tech', []))
                
                main_result['extracted_data']['links'] = list(set(all_links))
                main_result['extracted_data']['images'] = all_images
                main_result['extracted_data']['headings'] = all_headings
                main_result['extracted_data']['detected_tech'] = list(set(all_tech))
            
            main_result['metadata']['page_count'] = len([r for r in results if r['success']])
            main_result['crawl_results'] = results if depth > 0 else None
            
            return main_result
        
        return {
            'success': False,
            'url': start_url,
            'error': 'No pages scraped',
            'error_type': 'no_results'
        }

def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            'success': False,
            'error': 'Usage: python web-scraper.py \'{"url": "https://example.com", "depth": 1}\''
        }), file=sys.stderr)
        sys.exit(1)
    
    try:
        # Parse input
        config = json.loads(sys.argv[1])
        url = config.get('url')
        depth = config.get('depth', 0)
        
        if not url:
            raise ValueError('URL is required')
        
        # Create scraper and run
        scraper = WebScraper()
        result = scraper.crawl(url, depth)
        
        # Output result
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['success'] else 1)
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e),
            'error_type': 'unexpected_error'
        }), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
