#!/usr/bin/env python3
"""
Full Excel -> Email scraper.
- Input Excel: companies.xlsx (first column = company names or domains)
- Output Excel: email_results.xlsx
"""

import sys, subprocess, os, re, time
def _ensure_packages(pkgs):
    import importlib
    for p in pkgs:
        try:
            importlib.import_module(p)
        except ImportError:
            print(f"[+] Installing {p} ...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])

# Ensure required packages
_ensure_packages(["pandas", "openpyxl", "requests", "beautifulsoup4", "urllib3"])

import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures

# -----------------------------
# Email extraction helpers
# -----------------------------
EMAIL_REGEX = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,63}')
OBFUS_PATTERNS = [
    (r'\s*\(at\)\s*', '@'), (r'\s*\[at\]\s*', '@'), (r'\s+at\s+', '@'),
    (r'\s*\(dot\)\s*', '.'), (r'\s*\[dot\]\s*', '.'), (r'\s+dot\s+', '.')
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}

def deobfuscate(text: str) -> str:
    t = text
    for pat, rep in OBFUS_PATTERNS:
        t = re.sub(pat, rep, t, flags=re.IGNORECASE)
    return t

def extract_emails_from_text(text: str):
    text = deobfuscate(text or "")
    found = set(m.group(0).strip('.,;:<>\"\'()[]{}') for m in EMAIL_REGEX.finditer(text))
    return {e.lower() for e in found if '@' in e}

def get_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429,500,502,503,504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s

def normalize_domain(raw):
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if not s or s in ("nan", "none"):
        return None
    s = s.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0]
    if "." in s:
        return s
    return s + ".com"

# -----------------------------
# Scraping functions
# -----------------------------
def get_page_content(session, url, timeout=12):
    try:
        r = session.get(url, timeout=timeout)
        ct = r.headers.get("Content-Type", "")
        if r.status_code == 200 and "text/html" in ct:
            return r.text
    except Exception:
        return None
    return None

def find_all_internal_links(session, url, domain):
    content = get_page_content(session, url)
    if not content:
        return []
    soup = BeautifulSoup(content, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a['href'].strip()
        full = urljoin(url, href)
        parsed = urlparse(full)
        netloc = parsed.netloc.lower()
        if netloc.endswith(domain):
            if parsed.path.lower().endswith(('.pdf','.jpg','.png','.zip','.doc','.docx','.xls','.xlsx','.svg')):
                continue
            full = full.split('#')[0]
            links.add(full)
    return list(links)

def scrape_page_for_emails(session, url):
    emails = set()
    content = get_page_content(session, url)
    if not content:
        return emails
    emails.update(extract_emails_from_text(content))
    soup = BeautifulSoup(content, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.startswith("mailto:"):
            mail = href[7:].split("?")[0].strip()
            mail = deobfuscate(mail)
            if "@" in mail:
                emails.add(mail.lower())
    return emails

def deep_scrape_domain(session, domain, max_pages=50, max_workers=10, verbose=True):
    results = set()
    base_candidates = [f"https://{domain}", f"http://{domain}"]
    start_url = None
    for candidate in base_candidates:
        if get_page_content(session, candidate):
            start_url = candidate
            break
    if not start_url:
        if verbose:
            print(f"[WARN] {domain} unreachable.")
        return results

    if verbose:
        print(f"[INFO] Starting scan: {start_url}")

    try:
        results.update(scrape_page_for_emails(session, start_url))
    except Exception:
        pass

    internal_links = find_all_internal_links(session, start_url, domain)
    if verbose:
        print(f"[INFO] Found {len(internal_links)} internal links (scan up to {max_pages})")

    keywords = ['contact','about','support','help','team','staff','careers','job','press','media','contact-us']
    important = [u for u in internal_links if any(k in u.lower() for k in keywords)]
    other = [u for u in internal_links if u not in important]

    scan_list = [start_url] + important[:20] + other[:max_pages - 1 - len(important[:20])]
    scan_list = list(dict.fromkeys(scan_list))

    if verbose:
        print(f"[INFO] Scanning {len(scan_list)} pages for {domain}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_page_for_emails, session, url): url for url in scan_list}
        for fut in concurrent.futures.as_completed(futures):
            url = futures[fut]
            try:
                emails = fut.result()
                if emails and verbose:
                    print(f"   ✅ {len(emails)} email(s) at {url}")
                results.update(emails)
            except Exception:
                continue

    return results

# -----------------------------
# Excel processing
# -----------------------------
def process_companies_from_excel(input_file="companies.xlsx", output_file="email_results.xlsx",
                                 first_n=None, max_pages=50, max_workers=10):
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file not found: {input_file}")
        return

    df = pd.read_excel(input_file, engine="openpyxl")
    if df.shape[1] == 0:
        print("[ERROR] Input Excel appears empty.")
        return

    company_list = df[df.columns[0]].dropna().astype(str).tolist()
    session = get_session()
    results = []

    total = len(company_list) if first_n is None else min(len(company_list), first_n)
    for idx, raw in enumerate(company_list[:total], 1):
        domain = normalize_domain(raw)
        if not domain:
            print(f"[SKIP] Row {idx}: empty/invalid input.")
            continue
        print(f"\n=== ({idx}/{total}) Scanning: {raw} -> {domain} ===")
        start = time.time()
        try:
            emails = deep_scrape_domain(session, domain, max_pages=max_pages, max_workers=max_workers)
        except Exception:
            emails = set()
        elapsed = time.time() - start

        if emails:
            for e in sorted(emails):
                results.append({"Input": raw, "Domain": domain, "Email": e, "TimeTaken_s": round(elapsed, 2)})
        else:
            results.append({"Input": raw, "Domain": domain, "Email": "", "TimeTaken_s": round(elapsed, 2)})

    out_df = pd.DataFrame(results)
    out_df.to_excel(output_file, index=False, engine="openpyxl")
    print(f"\n✅ Finished. Results saved to: {output_file} (rows: {len(out_df)})")

# -----------------------------
# CLI entry
# -----------------------------
if __name__ == "__main__":
    print("Excel -> Email Scraper")
    inp = input("Input Excel file (default companies.xlsx): ").strip() or "companies.xlsx"
    out = input("Output Excel file (default email_results.xlsx): ").strip() or "email_results.xlsx"
    try:
        n = input("Scan first how many rows? (Enter = all): ").strip()
        first_n = int(n) if n else None
    except:
        first_n = None

    process_companies_from_excel(input_file=inp, output_file=out, first_n=first_n)
