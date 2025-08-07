
import os
import requests
from bs4 import BeautifulSoup

def download_images_from_url(url, folder_name):
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        os.makedirs(folder_name, exist_ok=True)
        imgs = soup.find_all("img")
        for index, img in enumerate(imgs, start=1):
            img_url = img.get("src")
            if not img_url:
                continue
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            elif img_url.startswith("/"):
                img_url = url.split("/series/")[0] + img_url
            elif not img_url.startswith("http"):
                continue
            try:
                img_data = requests.get(img_url).content
                with open(os.path.join(folder_name, f"image_{index}.jpg"), "wb") as f:
                    f.write(img_data)
            except:
                pass
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")

def main():
    try:
        with open("links.txt", "r", encoding="utf-8") as file:
            urls = file.read().splitlines()
    except FileNotFoundError:
        print("File 'links.txt' not found.")
        return

    for url in urls:
        if not url.strip():
            continue
        page_number = url.strip().split("/")[-1]
        print(f"Downloading page {page_number} ...")
        download_images_from_url(url, os.path.join("downloads", page_number))

    print("✅ Done downloading all pages!")

if __name__ == "__main__":
    main()
