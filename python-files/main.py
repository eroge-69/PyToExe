from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import re
import time

# Kullanıcıdan ad-soyad al
ad = input("Ad: ").strip()
soyad = input("Soyad: ").strip()

ad_encoded = ad.replace(" ", "%20")
soyad_encoded = soyad.replace(" ", "%20")

api_url = f"http://nailleh.fwh.is/api/okul.php?ad={ad_encoded}&soyad={soyad_encoded}"
print(f"Tarayıcıda açılıyor: {api_url}")

chrome_options = Options()
chrome_options.add_argument("--headless")  # İstersen gizli aç
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.get(api_url)
    time.sleep(2)

    html = driver.page_source

    # HTML içindeki JSON'u ayıkla
    # <pre>...</pre> içinde geliyor
    match = re.search(r"<pre[^>]*>(.*?)</pre>", html, re.DOTALL | re.IGNORECASE)
    if match:
        json_raw = match.group(1).strip()
        try:
            data = json.loads(json_raw)
            print(json.dumps(data, indent=4, ensure_ascii=False))
        except json.JSONDecodeError:
            print("JSON parse edilemedi! Gelen ham veri:")
            print(json_raw)
    else:
        print("JSON <pre> etiketi içinde bulunamadı!")
        print("Tam HTML:")
        print(html)

finally:
    driver.quit()
