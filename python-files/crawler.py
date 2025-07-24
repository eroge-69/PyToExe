#!C:/Python313/python.exe
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')

from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import pytz
import hashlib
import psutil

# 🌀 HTML Header
print("Content-Type: text/html; charset=utf-8\n")
print("<html><head><title>Luumyn Crawler Activated</title>")
print("<style>body{background:#111;color:#eee;font-family:monospace;padding:1em;}a{color:#9cf;}p{margin:0.3em 0;}hr{border:0;border-top:1px solid #333;}strong{color:#cff;}#fixed-header{position:sticky;top:0;background:#222;border-bottom:1px solid #444;padding:0.5em 1em;font-size:14px;color:#9cf;display:flex;justify-content:space-between;align-items:center;}</style></head><body>")
print("<h1>Luumyn Crawler Activated</h1><hr>")
print("<p style='color:#fc6;'>🧪 [Debug] Luumyn Crawler script began running</p>")

# 🌀 Progress UI with Live RAM
initial_ram = psutil.Process(os.getpid()).memory_info().rss / 1048576

print(f"""
Content-Type: text/html; charset=utf-8

<html>
<head>
  <title>Luumyn Crawler Activated</title>
  <style>
    body {{ background:#111; color:#eee; font-family:monospace; padding:1em; }}
    a {{ color:#9cf; }}
    p {{ margin:0.3em 0; }}
    hr {{ border:0; border-top:1px solid #333; }}
    strong {{ color:#cff; }}
    #fixed-header {{
      position:sticky;
      top:0;
      background:#222;
      border-bottom:1px solid #444;
      padding:0.5em 1em;
      font-size:14px;
      color:#9cf;
      display:flex;
      justify-content:space-between;
      align-items:center;
      z-index:10;
    }}
  </style>
</head>
<body>

<h1>Luumyn Crawler Activated</h1><hr>
<p style='color:#fc6;'>🧪 [Debug] Luumyn Crawler script began running</p>

<div id='fixed-header'>
  <div>🧭 Indexing Progress: <span id='count'>0</span> URLs</div>
  <div>🧠 RAM Usage: <span id='ram'>{initial_ram:.2f}</span> MB</div>
</div>

<script>
function updateCount(n) {{
  document.getElementById('count').textContent = n;
}}
function updateRAM(mb) {{
  document.getElementById('ram').textContent = mb.toFixed(2);
}}
</script>
""")

HEADERS = { "User-Agent": "LuumynOSCrawler/3.0 (+https://luumyn.space)" }

seed_path = "D:/xampp/htdocs/search/admin/seed_urls.json"
index_path = "D:/xampp/htdocs/search/admin/index.json"  # Line-delimited format
tz = pytz.timezone("Pacific/Auckland")
MAX_DEPTH = 1
visited = set()
results = []
existing_urls = set()
existing_hashes = {}
indexed_count = 0

def get_content_hash(html):
    return hashlib.md5(html.encode("utf-8")).hexdigest()

# ✅ Load existing index line-by-line
if os.path.exists(index_path):
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                url = entry.get("url")
                hash = entry.get("content_hash")
                if url:
                    existing_urls.add(url)
                    results.append(entry)
                    if hash:
                        existing_hashes[url] = hash
        print(f"<p style='color:#6f6;'>✅ [Loaded] {len(existing_urls)} existing entries preserved.</p>")
    except Exception as e:
        print(f"<p style='color:#f88;'>❌ [Error] Failed to load index: {e}</p>")

# 🧬 Load seed URLs
try:
    with open(seed_path, "r", encoding="utf-8") as f:
        SEED_URLS = json.load(f)
        print(f"<p style='color:#fc6;'>🧪 [Debug] Seed URLs retrieved: {len(SEED_URLS)}</p>")
except Exception as e:
    print(f"<p style='color:#f88;'>❌ [Error] Failed to load seed URLs: {e}</p>")
    SEED_URLS = []

ALLOWED_DOMAINS = [urlparse(u).netloc for u in SEED_URLS]
print(f"<p style='color:#fc6;'>🧪 [Debug] Allowed domains: {ALLOWED_DOMAINS}</p>")
start_time = datetime.now(tz).strftime("%d %B %Y • %I:%M %p NZST")
print(f"<div style='color:#ccc;'>⏱ Crawl started at: {start_time} • Initial entries: <strong>{len(results)}</strong></div><hr>")

def is_valid(url):
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and parsed.netloc in ALLOWED_DOMAINS

def extract_description(soup):
    tag = soup.find("meta", attrs={"name": "description"})
    return tag.get("content").strip() if tag and tag.get("content") else ""

def extract_image(soup):
    tag = soup.find("meta", property="og:image")
    return tag.get("content").strip() if tag and tag.get("content") else ""

def crawl(url, depth=0, path=None):
    global indexed_count
    if url in visited or depth > MAX_DEPTH:
        return

    path = (path or []) + [url]
    print(f"<p style='color:#9cf;'>🔍 [Crawling • Depth {depth}] <a href='{url}' target='_blank'>{url}</a></p>")

    try:
        res = requests.get(url, headers=HEADERS, timeout=6)
        ctype = res.headers.get("Content-Type", "")
        if "text/html" not in ctype:
            print(f"<p style='color:#fc6;'>⚠️ [Skipped] Non-HTML content: {ctype}</p>")
            return

        content_hash = get_content_hash(res.text)
        if url in existing_hashes and existing_hashes[url] == content_hash:
            print(f"<p style='color:#777;'>⏸ [Unchanged] {url} — Skipped</p>")
            return

        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled"
        desc = extract_description(soup)
        image = extract_image(soup)
        domain = urlparse(url).netloc
        now = datetime.now(tz)

        entry = {
            "url": url,
            "title": title,
            "description": desc,
            "image": image,
            "domain": domain,
            "indexed_at": now.isoformat(),
            "indexed_display": now.strftime("%d %B %Y • %I:%M %p NZST"),
            "content_hash": content_hash
        }

        results.append(entry)
        visited.add(url)
        indexed_count += 1

        # 🧭 Update UI and RAM display
        print(f"<script>updateCount({indexed_count});</script>")
        current_ram = psutil.Process(os.getpid()).memory_info().rss / 1048576
        print(f"<script>updateRAM({current_ram});</script>")
        print(f"<p style='color:#6f6;'>✅ [Indexed] <strong>{title}</strong> — {domain} • <span style='color:#aff;'>🔢 {indexed_count}</span></p>")

        for link in soup.find_all("a", href=True):
            absolute = urljoin(url, link["href"])
            if is_valid(absolute):
                crawl(absolute, depth + 1, path)

    except Exception as e:
        print(f"<p style='color:#f88;'>❌ [Error] Crawling failed for {url}: {e}</p>")

# 🔁 Begin crawl
for seed in SEED_URLS:
    crawl(seed)

print("<p style='color:#fc6;'>🧪 [Debug] All seed URLs processed</p>")

# 💾 Save updated index line-by-line
try:
    with open(index_path, "w", encoding="utf-8") as f:
        for entry in results:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    new_entries = len(results) - len(existing_urls)
    print(f"<hr><p style='color:#9f9;'>✅ Crawl Complete</p>")
    print(f"<p style='color:#aff;'>🔗 Total Indexed: <strong>{len(results)}</strong></p>")
    print(f"<p style='color:#6ff;'>➕ New Entries Added: <strong>{new_entries}</strong></p>")
except Exception as e:
    print(f"<p style='color:#f88;'>❌ [Error] Saving index: {e}</p>")

print("</body></html>")
