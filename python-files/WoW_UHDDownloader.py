
#!/usr/bin/env python3
"""
WoW UHDPaper 4K Wallpaper Downloader & Zipper
- Crawls uhdpaper.com for wallpapers (optionally limited by search query)
- Downloads images, filters those with resolution >= 3840x2160 (4K)
- Saves images into a folder and creates a ZIP archive
- Usage: python WoW_UHDDownloader.py --query "World of Warcraft" --out wow_wallpapers.zip

Notes / requirements:
    pip install requests beautifulsoup4 pillow tqdm
Important:
    Use this tool for personal use only and respect copyright / terms of the site.
"""

import os
import re
import sys
import time
import argparse
import zipfile
from io import BytesIO
from urllib.parse import urljoin, urlparse, quote_plus

import requests
from bs4 import BeautifulSoup
from PIL import Image
from tqdm import tqdm

USER_AGENT = "WoW-UHD-Downloader/1.0 (+https://example.com)"
BASE = "https://www.uhdpaper.com"

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def fetch(url, **kwargs):
    try:
        r = session.get(url, timeout=20, **kwargs)
        r.raise_for_status()
        return r
    except Exception as e:
        print(f"[!] Failed to fetch {url}: {e}")
        return None


def find_search_pages(query, max_pages=50):
    """
    Generator that yields search result pages for the given query.
    uhdpaper search URL often: /search?q=...&by-date=true&page=2
    We'll iterate pages until no new results or max_pages reached.
    """
    q = quote_plus(query)
    page = 1
    seen_urls = set()
    while page <= max_pages:
        search_url = f"{BASE}/search?q={q}&by-date=true&page={page}"
        r = fetch(search_url)
        if not r:
            break
        soup = BeautifulSoup(r.text, "html.parser")
        results = soup.select("a[href*='/20']")  # often posts have /YYYY/
        found_any = False
        for a in results:
            href = a.get("href")
            if not href:
                continue
            full = urljoin(BASE, href)
            if full not in seen_urls and "/20" in full:
                seen_urls.add(full)
                found_any = True
                yield full
        if not found_any:
            break
        page += 1
        time.sleep(0.5)
    return


def extract_image_urls_from_page(page_url):
    """
    Parse a wallpaper post page and extract candidate full-size image URLs.
    uhdpaper often contains <a class="download" href="..."> or <img src="...">
    """
    r = fetch(page_url)
    if not r:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    imgs = set()

    # Common: direct image tags
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src") or img.get("data-lazy-src")
        if src and src.strip():
            imgs.add(urljoin(page_url, src.strip()))

    # Also look for download links or anchors that link to image files .jpg/.png/.webp
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if re.search(r"\.(jpe?g|png|webp|bmp)$", href, re.I):
            imgs.add(urljoin(page_url, href))

    # Heuristic: sometimes the largest image is inside a <div class="post-body"> with background images
    for div in soup.find_all(style=True):
        style = div.get("style", "")
        m = re.search(r"url\(([^)]+)\)", style)
        if m:
            url = m.group(1).strip("'\" ")
            imgs.add(urljoin(page_url, url))
    # Return unique
    return list(imgs)


def is_4k_image(content_bytes):
    try:
        with Image.open(BytesIO(content_bytes)) as im:
            w, h = im.size
            return (w >= 3840 and h >= 2160) or (w >= 2160 and h >= 3840)
    except Exception:
        return False


def download_image(url, out_dir, filename=None, verify_4k=True):
    r = fetch(url, stream=True)
    if not r:
        return None, False
    try:
        data = r.content
        if verify_4k:
            if not is_4k_image(data):
                return None, False
        if not filename:
            path = urlparse(url).path
            filename = os.path.basename(path) or f"img_{int(time.time()*1000)}.jpg"
        filename = re.sub(r"[\\/:*?\"<>|]", "_", filename)
        out_path = os.path.join(out_dir, filename)
        with open(out_path, "wb") as f:
            f.write(data)
        return out_path, True
    except Exception as e:
        print(f"[!] Error saving {url}: {e}")
        return None, False


def make_zip(folder, zipname):
    with zipfile.ZipFile(zipname, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(folder):
            for fname in files:
                full = os.path.join(root, fname)
                arcname = os.path.relpath(full, folder)
                zf.write(full, arcname)
    return zipname


def main(args):
    out_dir = args.output_folder
    os.makedirs(out_dir, exist_ok=True)

    if args.urls:
        pages = args.urls
    else:
        print("[*] Discovering pages via search...")
        pages = list(find_search_pages(args.query, max_pages=args.max_pages))
        print(f"[*] Found {len(pages)} pages from search.")

    all_image_urls = set()
    for p in tqdm(pages, desc="Parsing pages"):
        try:
            urls = extract_image_urls_from_page(p)
            for u in urls:
                all_image_urls.add(u)
        except Exception as e:
            print(f"[!] Error parsing {p}: {e}")
        time.sleep(0.2)

    print(f"[*] {len(all_image_urls)} candidate image URLs found. Filtering & downloading 4K...")

    downloaded = []
    for img_url in tqdm(sorted(all_image_urls), desc="Downloading"):
        out_path, ok = download_image(img_url, out_dir, verify_4k=not args.skip_verify)
        if ok and out_path:
            downloaded.append(out_path)
        time.sleep(0.15)

    print(f"[*] Downloaded {len(downloaded)} images to {out_dir}")

    if args.zipname:
        zip_path = make_zip(out_dir, args.zipname)
        print(f"[*] ZIP created: {zip_path}")

    print("[*] Done. Please check images for quality and licensing before public use.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="UHDPaper 4K Wallpaper downloader & zipper")
    ap.add_argument("--query", default="World of Warcraft", help="Search query to find post pages on uhdpaper.com")
    ap.add_argument("--max-pages", type=int, default=40, help="Max search pages to crawl")
    ap.add_argument("--output-folder", default="wallpapers_uhdpaper", help="Folder to save images into")
    ap.add_argument("--zipname", default="wallpapers_uhdpaper.zip", help="Create this ZIP from the download folder (optional)")
    ap.add_argument("--skip-verify", action="store_true", help="Skip verifying images are >=4K (faster)")
    ap.add_argument("--urls", nargs='*', help="Optional: list of post URLs to parse directly (overrides search)")
    args = ap.parse_args()
    main(args)
