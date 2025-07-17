
import requests
from bs4 import BeautifulSoup
from forex_python.converter import CurrencyRates

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_usd_to_cad():
    c = CurrencyRates()
    return c.get_rate('USD', 'CAD')

def scrape_amazon_price(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.select_one('#priceblock_ourprice, #priceblock_dealprice')
        if price_tag:
            price_text = price_tag.text.strip().replace('$', '').replace(',', '')
            return float(price_text)
    except Exception as e:
        print("Hata:", e)
    return None

def calculate_profit(usd_price, cad_price, usd_to_cad):
    converted = usd_price * usd_to_cad
    kar = cad_price - converted
    kar_yuzde = (kar / converted) * 100 if converted != 0 else 0
    return round(kar, 2), round(kar_yuzde, 2)

# ÖRNEK: Test ürünleri
amazon_us_url = "https://www.amazon.com/dp/B0CGLM7GH7"
amazon_ca_url = "https://www.amazon.ca/dp/B0CGLM7GH7"

usd_price = scrape_amazon_price(amazon_us_url)
cad_price = scrape_amazon_price(amazon_ca_url)
usd_to_cad = get_usd_to_cad()

if usd_price and cad_price:
    kar, yuzde = calculate_profit(usd_price, cad_price, usd_to_cad)
    print(f"ABD Fiyatı: ${usd_price}")
    print(f"Kanada Fiyatı: ${cad_price}")
    print(f"Canlı kur: 1 USD = {usd_to_cad:.2f} CAD")
    print(f"Kâr: {kar} CAD ({yuzde}%)")
else:
    print("Fiyat verisi alınamadı.")
