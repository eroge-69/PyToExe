#!/usr/bin/env python3

import sys
import subprocess

def install(pkg):
    """Install a package via pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

# Ensure dependencies are installed
for pkg, mod in (
    ("requests",       "requests"),
    ("beautifulsoup4", "bs4"),
    ("tqdm",           "tqdm"),
):
    try:
        __import__(mod)
    except ImportError:
        print(f"Installing {pkg}…")
        install(pkg)

import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm

# Base URL of the directory
BASE_URL = "https://opendir.samicrusader.me/Steam2/storages/"

# DepotID range to download
MIN_DEPOT_ID = 0
MAX_DEPOT_ID = 5212

# Folder where downloads will be saved
DOWNLOAD_DIR = "downloads"

def get_tar_entries(base_url, min_id, max_id):
    """
    Fetch the HTML listing, parse all .tar links with their DepotID,
    filter by the given range (without regex), and return a sorted list.
    """
    resp = requests.get(base_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    entries = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        if not href.lower().endswith(".tar"):
            continue

        # Extract "[DepotID ####]" by manual string search
        text = link.parent.get_text(separator=" ", strip=True)
        marker = "[DepotID "
        if marker not in text:
            continue

        start = text.index(marker) + len(marker)
        end = text.find("]", start)
        if end == -1:
            continue

        id_str = text[start:end].strip()
        if not id_str.isdigit():
            continue

        depot_id = int(id_str)
        if depot_id < min_id or depot_id > max_id:
            continue

        entries.append({
            "depotid":  depot_id,
            "url":      urljoin(base_url, href),
            "filename": os.path.basename(href),
        })

    # Sort by DepotID ascending
    return sorted(entries, key=lambda e: e["depotid"])


def download_file(entry, dest_folder):
    """
    Stream-download a file entry, showing progress, into dest_folder.
    Returns the depot ID and filename.
    """
    os.makedirs(dest_folder, exist_ok=True)
    local_path = os.path.join(dest_folder, entry["filename"])

    with requests.get(entry["url"], stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(local_path, "wb") as f, tqdm(
            total=total,
            unit="iB",
            unit_scale=True,
            desc=f"[DepotID {entry['depotid']}] {entry['filename']}"
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))

    return entry["depotid"], entry["filename"]


def main():
    print(f"Fetching .tar entries from {BASE_URL}")
    entries = get_tar_entries(BASE_URL, MIN_DEPOT_ID, MAX_DEPOT_ID)

    if not entries:
        print("No matching .tar files found in the given DepotID range.")
        return

    for entry in entries:
        print(f"\nStarting download: [DepotID {entry['depotid']}] {entry['filename']}")
        depot_id, fname = download_file(entry, DOWNLOAD_DIR)
        if depot_id == MAX_DEPOT_ID:
            print(f"\nReached target DepotID {MAX_DEPOT_ID}, stopping.")
            break

    print("\nAll done!")


if __name__ == "__main__":
    main()
