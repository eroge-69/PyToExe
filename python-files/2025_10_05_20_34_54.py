import requests
from bs4 import BeautifulSoup
import os
import csv
from urllib.parse import urljoin, urlparse

def save_image(image_url, folder="images"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    response = requests.get(image_url)
    if response.status_code == 200:
        filename = os.path.join(folder, os.path.basename(urlparse(image_url).path))
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    return None

def scrape_adwile_teasers(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    block = soup.find("div", class_="smi24__informer smi24__auto")
    if not block:
        print("Рекламный блок smi24__informer smi24__auto не найден")
        return

    teasers = []
    for item in block.find_all(recursive=False):
        img_tag = item.find("img")
        title_tag = item.find(["h1","h2","h3","h4","h5","span","a"])
        if img_tag and title_tag:
            img_url = urljoin(url, img_tag.get("src"))
            title = title_tag.get_text(strip=True)
            image_path = save_image(img_url)
            teasers.append({"title": title, "image_url": img_url, "image_path": image_path})

    with open("teasers.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["title", "image_url", "image_path"])
        writer.writeheader()
        for teaser in teasers:
            writer.writerow(teaser)
    print(f"Сохранено {len(teasers)} тизеров. Картинки в папке images, данные в teasers.csv")

if __name__ == "__main__":
    site_url = input("Введите URL сайта для сканирования: ")
    scrape_adwile_teasers(site_url)