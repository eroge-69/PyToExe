
import os
import re
import json
import time
from urllib.request import Request, urlopen
from urllib.parse import urljoin
from urllib.error import HTTPError, URLError

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

WINDOWS_EXTENSIONS = [".exe", ".msi", ".dll", ".bat", ".cmd", ".zip", ".iso"]

def is_windows_asset(filename):
    return any(filename.lower().endswith(ext) for ext in WINDOWS_EXTENSIONS)

def fetch(url, headers=None):
    req = Request(url, headers=headers or HEADERS)
    return urlopen(req)

def parse_listing(html):
    m = re.search(r"directLinkData\s*=\s*(\{.*?\});", html, re.DOTALL)
    if not m:
        raise RuntimeError("Could not find directLinkData in page")
    data = json.loads(m.group(1))
    return data.get("content", [])

def download_file(file_url, local_path, max_retries=3):
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    attempt = 0
    while attempt < max_retries:
        try:
            headers = HEADERS.copy()
            resume_byte_pos = 0

            if os.path.exists(local_path):
                resume_byte_pos = os.path.getsize(local_path)
                headers["Range"] = f"bytes={resume_byte_pos}-"

            req = Request(file_url, headers=headers)
            with urlopen(req) as resp, open(local_path, "ab") as out:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    out.write(chunk)

            print(f"      → saved: {local_path}")
            return
        except HTTPError as e:
            if e.code == 404:
                print(f"      ! 404 not found, skipping: {file_url}")
                return
            print(f"      ! HTTP error {e.code} for {file_url} (attempt {attempt+1})")
        except URLError as e:
            print(f"      ! URL error {e.reason} for {file_url} (attempt {attempt+1})")
        except Exception as e:
            print(f"      ! Unexpected error: {e} (attempt {attempt+1})")

        attempt += 1
        time.sleep(2 ** attempt)

    print(f"      ! Failed to download after {max_retries} attempts: {file_url}")

def download_directory(base_url, local_dir):
    print(f"→ scanning: {base_url}")
    os.makedirs(local_dir, exist_ok=True)

    try:
        html = fetch(base_url).read().decode("utf-8", errors="ignore")
    except HTTPError as e:
        print(f"  ! cannot open {base_url}: HTTP {e.code}")
        return
    except URLError as e:
        print(f"  ! cannot open {base_url}: {e.reason}")
        return

    try:
        items = parse_listing(html)
    except Exception as e:
        print(f"  ! parsing error at {base_url}: {e}")
        return

    for item in items:
        name = item["name"]
        enc = item["urlencodedname"]
        icon = item.get("icon", 0)

        if icon == 20:
            sub_url = urljoin(base_url, enc + "/")
            sub_dir = os.path.join(local_dir, name)
            print(f"  • entering dir: {name}/")
            download_directory(sub_url, sub_dir)
        else:
            if is_windows_asset(name):
                file_url = urljoin(base_url, enc)
                dest = os.path.join(local_dir, name)
                print(f"  • file: {name}")
                download_file(file_url, dest)
            else:
                print(f"      → skipping non-Windows asset: {name}")
