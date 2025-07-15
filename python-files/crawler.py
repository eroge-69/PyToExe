
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import sys

visited = set()
results = []

def crawl(url, depth, max_depth):
    if depth > max_depth or url in visited:
        return
    visited.add(url)
    try:
        response = requests.get(url, timeout=5)
        if 'text/html' not in response.headers.get('Content-Type', ''):
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
            if parsed.scheme.startswith('http'):
                results.append((url, full_url))
                crawl(full_url, depth + 1, max_depth)
    except Exception as e:
        print(f"Error crawling {url}: {e}")

def main(start_url, max_depth=2):
    crawl(start_url, 0, max_depth)
    df = pd.DataFrame(results, columns=['Source', 'Link'])
    df.to_excel('crawled_links.xlsx', index=False)
    print("Crawling complete. Output saved to 'crawled_links.xlsx'.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python crawler.py <URL> [depth]")
    else:
        start_url = sys.argv[1]
        depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        main(start_url, depth)
