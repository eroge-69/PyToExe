import requests
from bs4 import BeautifulSoup
import os
import re
import csv
import fitz  # PyMuPDF
from tqdm import tqdm

BASE_URL = "https://isrs.gov.cz"
START_URL = "https://isrs.gov.cz/smlouva/soubor/"
OUTPUT_CSV = "results.csv"
DOWNLOAD_DIR = "Downloaded_PDFs"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

visited = set()
pdf_links = set()

def get_links(url):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            link = a['href']
            if link.startswith("/"):
                link = BASE_URL + link
            if link.startswith(BASE_URL):
                links.append(link)
        return links
    except:
        return []

def crawl(url, depth=0, max_depth=3):
    if url in visited or depth > max_depth:
        return
    visited.add(url)
    links = get_links(url)
    for link in links:
        if link.endswith(".pdf"):
            pdf_links.add(link)
        elif link.startswith(BASE_URL):
            crawl(link, depth + 1, max_depth)

def download_pdf(url):
    local_filename = os.path.join(DOWNLOAD_DIR, url.split("/")[-1])
    if not os.path.exists(local_filename):
        try:
            resp = requests.get(url, timeout=20)
            with open(local_filename, "wb") as f:
                f.write(resp.content)
        except:
            return None
    return local_filename

def pdf_contains_keywords(filepath, keywords):
    try:
        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return all(re.search(rf"\b{re.escape(k)}\b", text, re.IGNORECASE) for k in keywords)
    except:
        return False

if __name__ == "__main__":
    print("[*] Crawling website...")
    crawl(START_URL)
    print(f"[*] Found {len(pdf_links)} PDF files. Checking contents...")
    results = []
    for link in tqdm(pdf_links, desc="Processing PDFs"):
        local_file = download_pdf(link)
        if not local_file:
            continue
        if pdf_contains_keywords(local_file, ["Grant Agreement", "Erasmus"]):
            results.append([link, os.path.basename(local_file), "Yes"])
        else:
            results.append([link, os.path.basename(local_file), "No"])
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Filename", "Contains Keywords"])
        writer.writerows(results)