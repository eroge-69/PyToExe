import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

def scrape_hifilife(url):
    print(f"🔍 Sayfa inceleniyor: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print("❌ Sayfa yüklenemedi.")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Ürün adı
    title = soup.find("h1")
    product_name = title.get_text(strip=True) if title else "Ürün Adı Bulunamadı"

    # Fiyat
    price_tag = soup.find(class_="price")
    price = price_tag.get_text(strip=True) if price_tag else "Fiyat bulunamadı"

    # Açıklama
    desc_tag = soup.find(class_="product-short-description") or soup.find(class_="woocommerce-product-details__short-description")
    description = desc_tag.get_text("\n", strip=True) if desc_tag else "Açıklama bulunamadı"

    # Resimler
    image_tags = soup.find_all("img")
    image_urls = []
    for img in image_tags:
        src = img.get("src")
        if src and ("hifilife.com" in src or src.startswith("/")) and not src.endswith(".svg"):
            full_url = urljoin(url, src)
            if full_url not in image_urls:
                image_urls.append(full_url)

    # Klasör oluştur
    folder_name = f"Hifilife_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(folder_name, exist_ok=True)
    img_folder = os.path.join(folder_name, "images")
    os.makedirs(img_folder, exist_ok=True)

    # Bilgileri kaydet
    with open(os.path.join(folder_name, "urun_bilgileri.txt"), "w", encoding="utf-8") as f:
        f.write(f"Ürün Adı: {product_name}\n")
        f.write(f"Fiyat: {price}\n\n")
        f.write("Açıklama:\n")
        f.write(description + "\n\n")
        f.write("Resimler:\n")
        for img_url in image_urls:
            f.write(img_url + "\n")

    # Resimleri indir
    for i, img_url in enumerate(image_urls, start=1):
        try:
            img_data = requests.get(img_url).content
            ext = img_url.split(".")[-1].split("?")[0]
            img_path = os.path.join(img_folder, f"image_{i}.{ext}")
            with open(img_path, "wb") as img_file:
                img_file.write(img_data)
        except:
            pass

    print(f"✅ İşlem tamamlandı! Klasör: {folder_name}")

if __name__ == "__main__":
    product_url = input("Hifilife ürün linkini girin: ").strip()
    scrape_hifilife(product_url)