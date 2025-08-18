import os
import re
import requests
from bs4 import BeautifulSoup

DOWNLOAD_DIR = r"C:\Downloads"
URL_FILE = r"get_app.txt"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def find_download_link(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[LỖI] Không thể truy cập {url}: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    # Tìm link chứa exe/msi/zip
    link = soup.find("a", href=re.compile(r".*\.(exe|msi|zip)$", re.I))
    if link:
        href = link.get("href")
        if not href.startswith("http"):
            # nối domain nếu link là relative
            from urllib.parse import urljoin
            href = urljoin(url, href)
        return href
    return None

def download_file(url, folder=DOWNLOAD_DIR):
    local_filename = url.split("/")[-1].split("?")[0]
    filepath = os.path.join(folder, local_filename)
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"[OK] Đã tải {local_filename}")
    except Exception as e:
        print(f"[LỖI] Không thể tải {url}: {e}")

def main():
    with open(URL_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]
    for url in urls:
        print(f"\n>>> Xử lý {url}")
        dl_link = find_download_link(url)
        if dl_link:
            print(f"    → Link tải: {dl_link}")
            download_file(dl_link)
        else:
            print("    [!] Không tìm thấy file setup trực tiếp trên trang này.")

if __name__ == "__main__":
    main()