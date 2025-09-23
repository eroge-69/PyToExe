import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import re

BASE_URL = "https://m.avito.ru/sankt-peterburg/kommercheskaya_nedvizhimost"

types = ['свободн', 'офис', 'склад', 'торгов']
map_to_full = {
    'свободн': 'Помещение свободного назначения',
    'офис': 'Офисное помещение',
    'склад': 'Складское помещение',
    'торгов': 'Торговая площадь',
}

def build_url(url: str) -> str:
    return f"http://api.scraperapi.com?api_key={SCRAPERAPI_KEY}&url={url}"

def get(url, retries=5):
    for attempt in range(retries):    
        payload = { 'api_key': '0b30deebe497dde5fe289d39c2150ab8', 'url': url, 'device_type': 'mobile' }
        try:
            resp = requests.get('https://api.scraperapi.com/', params=payload)
            if resp.status_code == 200:
                return resp
            elif resp.status_code == 429:
                wait = 100
                print(f"429 Too Many Requests, waiting {wait:.1f}s...")
                time.sleep(wait)
                continue
            else:
                print(f"Error {resp.status_code} on {url}. Retrying in 3 second")
                time.sleep(3)
        except requests.RequestException as e:
            print("Request failed:", e)
            time.sleep(2)
    return None

def extract_area(text: str) -> str:
    if not text:
        return None
    match_type = ['(\d+)', '(\d+(?:[,.]\d+)?)']

    match_naming = ['\s*м²', '\s*кв.?\s*м', '\s*м2']

    result = None
    for type in match_type:
        for name in match_naming:
            patt = rf"{type}{name}"
            match = re.search(patt, text)
            result = float(match.group(1).replace(',', '.')) if match else None
            if result:
                break
    return result

def clean_price(text: str) -> int:
    """Convert price string to integer (RUB)."""
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return float(digits) if digits else None

def extract_price(text: str):
    if not text:
        return None
    # Look for digits (with optional spaces in between) before the ₽ sign
    match = re.search(r'([\d\s\u00A0]+)\s*₽', text)
    if match:
        num_str = match.group(1)
        # Remove spaces / non-breaking spaces
        num_str = num_str.replace(" ", "").replace("\u00A0", "")
        return int(num_str)
    return None

def parse_page(page: int, url: str):
    url = f"{url}?p={page}"
    print(f"Fetching page {page}...")
    resp = get(url)
    if not resp:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("a[data-marker='item/link']")
    offers = []

    for card in cards:
        next_div_block = card.find_next_sibling('div')
        href = card.get("href")
        if not href:
            continue
        full_url = "https://m.avito.ru" + href

        title_tag = card.select_one("span[data-marker='item/link-text']")
        title = title_tag.get_text(strip=True) if title_tag else None

        price_tag = next_div_block.find("div", {"data-marker": "highlightedPriceLabelRich"})
        if not price_tag:
            price_tag = next_div_block.find("div", {"data-marker": "priceLabelRich"})
        price_tag_span = price_tag.find('span') if price_tag else None
        price_tag_div = price_tag.find('div') if price_tag else None
        price = price_tag_span.get_text(strip=True) if price_tag_span else (price_tag_div.get_text(strip=True) if price_tag_div else None)
        price = extract_price(price)

        price_per_m2_tag = next_div_block.find("div", {"data-marker": "normalizedPriceVerticalContainerRich"})
        price_per_m2_tag_div = price_per_m2_tag.find('div') if price_per_m2_tag else None
        price_per_m2_tag_span = price_per_m2_tag.find('span') if price_per_m2_tag else None
        price_per_m2 = price_per_m2_tag_div.get_text(strip=True) if price_per_m2_tag_div else (price_per_m2_tag_span.get_text(strip=True) if price_per_m2_tag_span else None)
        price_per_m2 = extract_price(price_per_m2)
        
        container_tag = next_div_block.find("div", {"data-marker": "leftChildrenVerticalContainer"})
        all_divs = container_tag.find_all('div') if container_tag else []
        location = None
        if len(all_divs) >= 2:
            location = all_divs[-2].text  # crude split before date     
        
        desc_tags = next_div_block.find_all("div", class_=re.compile("yOENR|RIyLO"))
        desc_texts = [d.get_text(" ", strip=True) for d in desc_tags] if desc_tags else None
        desc_text = max(desc_texts, key=len) if desc_texts else None

        area_m2 = extract_area(title) or extract_area(desc_text)

        area_type = None
        for type_curr in types:
            if type_curr in title.lower():
                area_type = type_curr
                break

        if not price and area_m2 and price_per_m2:
            price = area_m2 * price_per_m2
        if not price_per_m2 and price and area_m2:
            price_per_m2 = price // area_m2

        offers.append({
            "Ссылка": full_url,
            "Название": title,
            "Цена": price,
            "Цена за кв. метр": price_per_m2,
            "Адрес": location,
            "Площадь, кв. м.": area_m2,
            "Описание": desc_text,
            "Тип помещения": area_type
        })

    return offers

def parse_all(num):
    url = None
    if num == 1:
        url = BASE_URL + "/sdam"
    else:
        url = BASE_URL + "/prodam"
    all_offers = []
    page = 1
    while True:
        offers = parse_page(page, url)
        if not offers:
            print("No more offers, stopping.")
            break
        all_offers.extend(offers)
        page += 1
        time.sleep(random.uniform(2, 4))
    return all_offers


if __name__ == "__main__":
    print("Введите цифру для поиска определенного типа объявлений. 1 - аренда, 2 - продажа")
    num = int(input())
    print("Введите минимальную площадь помещения: ")
    min_area = float(input())
    print("Введите максимальную площадь помещения: ")
    max_area = float(input())
    offers = parse_all(num)
    df = pd.DataFrame(offers)
    filtered_offers = [item for item in offers if (lambda x: x["Площадь, кв. м."] is not None and min_area <= x["Площадь, кв. м."] <= max_area)(item)]
    df_filtered = pd.DataFrame(filtered_offers)
    with pd.ExcelWriter("avito_offers_all.xlsx") as writer:
        df.to_excel(writer, sheet_name="Все объявления", index=False)
        df_filtered.to_excel(writer, sheet_name="Отфильрованные объявления", index=False)  
    print(f"Результаты парсинга записаны в файл avito_offers.xlsx")
