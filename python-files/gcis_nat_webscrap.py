import re
import time
import pathlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin

BASE        = "https://data.gcis.nat.gov.tw"
CATALOG_URL = "/od/datacategory"
PAUSE_SEC   = 0.5
HEADERS     = {"User-Agent": "GCIS-Bulk-Downloader/1.1 (+https://example.com)"}
OID_RE      = re.compile(r'oid=([A-F0-9-]{36})', re.I)

def list_datasets(session, first_page):
    page_url = urljoin(BASE, first_page)
    while page_url:
        r = session.get(page_url, timeout=30)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select('a[href*="/od/detail"]'):
            m = OID_RE.search(a["href"])
            if m:
                yield a.get_text(strip=True), m.group(1)
        next_link = soup.select_one(
            'ul.pagination a[rel="next"], a[href*="?page="]:contains("下一頁")'
        )
        page_url = urljoin(BASE, next_link["href"]) if next_link else None

def get_csv_oid(session, detail_oid):
    url = f"{BASE}/od/detail?oid={detail_oid}"
    r   = session.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    a    = soup.find("a", class_="csv") or soup.find("a", onclick=re.compile(r"/od/file\?oid="))
    if not a:
        return None
    m = re.search(r"/od/file\?oid=([\w-]{36})", a.get("onclick", ""))
    return m.group(1) if m else None

def download_csv(session, file_oid, folder, default_name):
    url  = f"{BASE}/od/file?oid={file_oid}"
    resp = session.get(url, timeout=60, allow_redirects=True)
    resp.raise_for_status()
    cd = resp.headers.get("Content-Disposition", "")
    m  = re.search(r'filename\*?=[^"]*"(.*?)"', cd) or re.search(r'filename="?([^";]+)"?', cd)
    fname = unquote(m.group(1)) if m else default_name
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / fname
    if path.exists():
        stem, ext = path.stem, path.suffix
        i = 1
        while (folder / f"{stem}_{i}{ext}").exists():
            i += 1
        path = folder / f"{stem}_{i}{ext}"
    with open(path, "wb") as f:
        f.write(resp.content)
    return path

def sanitize(name):
    return re.sub(r'[\\/:*?"<>|]', "_", name)

def main():
    # 1. 讓使用者輸入想要儲存的資料夾
    default = pathlib.Path("./gcis_bulk_csv").resolve()
    user_input = input(f"請輸入下載儲存路徑 (預設：{default})：").strip()
    if user_input:
        OUT_DIR = pathlib.Path(user_input).expanduser().resolve()
    else:
        OUT_DIR = default

    print("🚩 下載將存放於：", OUT_DIR, "\n")
    with requests.Session() as s:
        s.headers.update(HEADERS)
        datasets = list(list_datasets(s, CATALOG_URL))
        total = len(datasets)
        print(f"偵測到 {total} 筆資料集，開始批次下載…\n")

        for idx, (title, oid) in enumerate(datasets, 1):
            prefix = f"[{idx:>4}/{total}] {title[:40]:<40}"
            try:
                file_oid = get_csv_oid(s, oid)
                if not file_oid:
                    print(prefix, "SKIP ─ 無 CSV")
                else:
                    dst = download_csv(
                        s,
                        file_oid,
                        OUT_DIR,
                        f"{sanitize(title)}.csv",
                    )
                    print(prefix, f"OK   → {dst.name}")
            except Exception as e:
                print(prefix, f"FAIL ─ {e}")
            time.sleep(PAUSE_SEC)

if __name__ == "__main__":
    main()
