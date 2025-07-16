
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import sys

visited = set()
results = []

def crawl(url, base_url, depth=0, max_depth=3):
    if url in visited or depth > max_depth:
        return
    visited.add(url)
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results.append({
            "URL": url,
            "Status Code": response.status_code,
            "Title": soup.title.string if soup.title else "N/A",
            "Depth": depth
        })
        for link in soup.find_all("a", href=True):
            new_url = urljoin(base_url, link["href"])
            if base_url in new_url and urlparse(new_url).scheme in ["http", "https"]:
                crawl(new_url, base_url, depth + 1, max_depth)
    except Exception as e:
        results.append({
            "URL": url,
            "Status Code": "Error",
            "Title": str(e),
            "Depth": depth
        })

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: CARSGPT_Website_Crawler.exe <URL>")
        sys.exit(1)
    start_url = sys.argv[1]
    crawl(start_url, start_url)
    df = pd.DataFrame(results)
    df.to_excel("CARSGPT_Crawl_Results.xlsx", index=False)
    print("Crawl complete. Output saved to CARSGPT_Crawl_Results.xlsx")
