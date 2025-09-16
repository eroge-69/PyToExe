#!/usr/bin/env python3
"""
Amazon Ad Tool
- Paste an Amazon product page URL
- Downloads up to 8 product images
- Generates a simple title + description with bullet points
- Adds "Pick up from Para Vista" at the end
- Saves images + listing.txt in an output folder
"""

import os
import re
import json
import shutil
import threading
from urllib.parse import urljoin
from datetime import datetime
from tkinter import Tk, Label, Entry, Button, Text, END, filedialog, messagebox
import requests
from bs4 import BeautifulSoup

MAX_IMAGES = 8
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

def fetch_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text

def extract_image_urls(html):
    soup = BeautifulSoup(html, "html.parser")
    urls = []

    img = soup.find("img", id="landingImage")
    if img and img.get("data-a-dynamic-image"):
        try:
            data = json.loads(img["data-a-dynamic-image"])
            for u in data.keys():
                urls.append(u)
        except Exception:
            pass

    text = html
    for pat in [r'\"colorImages\"\s*:\s*(\{.*?\})',
                r'\"imageGalleryData\"\s*:\s*(\[{.*?}\])',
                r'\"imageUrl\"\s*:\s*\"(https?:\/\/[^\"]+)\"']:
        for m in re.finditer(pat, text, flags=re.DOTALL):
            block = m.group(1)
            found = re.findall(r'https?:\/\/[^"\',\]\} ]+\.(?:jpg|jpeg|png)', block)
            for f in found:
                urls.append(f)

    for i in soup.find_all("img"):
        src = i.get("src") or i.get("data-src") or ""
        if src and (("amazon" in src) or ("images" in src) or "media-amazon" in src):
            if re.search(r'\.(jpg|jpeg|png)', src, flags=re.IGNORECASE):
                urls.append(src)

    cleaned = []
    for u in urls:
        if not u:
            continue
        u = u.split("?")[0]
        if u.startswith("//"):
            u = "https:" + u
        if u not in cleaned:
            cleaned.append(u)
    return cleaned

def extract_title_and_bullets(html):
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find(id="productTitle") or soup.find("span", {"class":"a-size-large product-title-word-break"})
    title = title_tag.get_text(strip=True) if title_tag else ""

    bullets = []
    fb = soup.find(id="feature-bullets")
    if fb:
        for li in fb.find_all("li"):
            txt = li.get_text(" ", strip=True)
            if txt:
                bullets.append(clean_bullet(txt))

    if not bullets:
        alt = soup.find("div", {"id": "feature-bullets_feature_div"})
        if alt:
            for li in alt.find_all("li"):
                txt = li.get_text(" ", strip=True)
                if txt:
                    bullets.append(clean_bullet(txt))

    if not bullets:
        p = soup.find("div", {"id": "productDescription"})
        if p:
            text = p.get_text(" ", strip=True)
            parts = re.split(r'\.|\n', text)
            for s in parts:
                s = s.strip()
                if s and len(s) < 140:
                    bullets.append(clean_bullet(s))
                    if len(bullets) >= 5:
                        break

    final_bullets = []
    for b in bullets:
        b = re.sub(r'\s+', ' ', b).strip()
        if len(b) > 180:
            b = b[:177].rsplit(' ',1)[0] + "..."
        final_bullets.append(b)
        if len(final_bullets) >= 5:
            break

    return title, final_bullets

def clean_bullet(s):
    s = s.replace("\n", " ").strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'See more.*$', '', s, flags=re.IGNORECASE).strip()
    return s

def craft_title(short_title):
    base = short_title.strip()
    if not base:
        return "Brand New Item"
    words = base.split()
    short = " ".join(words[:6])
    return f"Brand New {short}"

def craft_description(bullets):
    lines = []
    if bullets:
        for b in bullets:
            b = b.strip().rstrip(".")
            lines.append(f"- {b}")
    else:
        lines.append("- Brand new, unused product.")
    lines.append("")
    lines.append("Pick up from Para Vista")
    return "\n".join(lines)

def download_images(urls, out_folder):
    os.makedirs(out_folder, exist_ok=True)
    saved = []
    for i, u in enumerate(urls[:MAX_IMAGES], start=1):
        ext = os.path.splitext(u)[1] or ".jpg"
        fname = os.path.join(out_folder, f"image_{i}{ext}")
        try:
            r = requests.get(u, headers=HEADERS, stream=True, timeout=20)
            r.raise_for_status()
            with open(fname, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            saved.append(fname)
        except Exception as e:
            print(f"Warning: failed to download {u}: {e}")
    return saved

class App:
    def __init__(self, root):
        self.root = root
        root.title("Amazon → Listing (Para Vista pickup)")
        root.geometry("640x360")
        Label(root, text="Paste Amazon product URL:").pack(pady=(10,0))
        self.url_entry = Entry(root, width=90)
        self.url_entry.pack(padx=10, pady=6)
        Button(root, text="Choose output folder (optional)", command=self.choose_folder).pack(pady=(0,6))
        self.out_label = Label(root, text="Output folder: (default will be Documents/AmazonListings_<date>)")
        self.out_label.pack()
        Button(root, text="Create listing", command=self.start_process).pack(pady=10)
        Label(root, text="Status / Preview:").pack(anchor="w", padx=10)
        self.status = Text(root, height=10, wrap='word')
        self.status.pack(fill='both', padx=10, pady=6, expand=True)
        Button(root, text="Open output folder", command=self.open_last_output).pack(pady=(0,10))
        self.chosen_folder = None
        self.last_output_folder = None

    def choose_folder(self):
        f = filedialog.askdirectory()
        if f:
            self.chosen_folder = f
            self.out_label.config(text=f"Output folder: {f}")

    def log(self, s):
        self.status.insert(END, s + "\n")
        self.status.see("end")

    def start_process(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste an Amazon product URL first.")
            return
        t = threading.Thread(target=self.process_link, args=(url,), daemon=True)
        t.start()

    def process_link(self, url):
        try:
            self.log("Fetching product page...")
            html = fetch_page(url)
        except Exception as e:
            self.log(f"Error fetching page: {e}")
            return

        self.log("Extracting title and features...")
        title_raw, bullets = extract_title_and_bullets(html)
        short_title = title_raw or ""
        title = craft_title(short_title)

        self.log(f"Product title (short): {short_title[:120]}")
        self.log("Finding images...")
        image_urls = extract_image_urls(html)
        if not image_urls:
            self.log("No images found automatically.")
        else:
            self.log(f"Found {len(image_urls)} image URLs, will download up to {MAX_IMAGES}.")

        base = self.chosen_folder if self.chosen_folder else os.path.join(os.path.expanduser("~"), "Documents")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_folder = os.path.join(base, f"AmazonListing_{stamp}")
        images_folder = os.path.join(out_folder, "images")
        os.makedirs(images_folder, exist_ok=True)

        saved = download_images(image_urls, images_folder)
        self.log(f"Downloaded {len(saved)} images to {images_folder}")

        desc = craft_description(bullets)

        listing_path = os.path.join(out_folder, "listing.txt")
        with open(listing_path, "w", encoding="utf-8") as f:
            f.write(title + "\n\n")
            f.write(desc + "\n")
            f.write("\nAmazon link: " + url + "\n")

        self.last_output_folder = out_folder
        self.log(f"Listing saved: {listing_path}")
        self.log("---- Listing preview ----")
        self.log(title)
        self.log("")
        for line in desc.splitlines():
            self.log(line)
        self.log("---- End preview ----")
        messagebox.showinfo("Done", f"Listing created in:\n{out_folder}\n\nOpen the folder to upload images and copy the text into Facebook Marketplace.")

    def open_last_output(self):
        if self.last_output_folder and os.path.exists(self.last_output_folder):
            try:
                if os.name == "nt":
                    os.startfile(self.last_output_folder)
                elif os.name == "posix":
                    os.system(f'xdg-open "{self.last_output_folder}"')
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {e}")
        else:
            messagebox.showwarning("No output yet", "No output folder has been created yet.")

def main():
    try:
        root = Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        print("Fatal error:", e)

if __name__ == "__main__":
    main()
