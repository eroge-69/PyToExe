import requests
from bs4 import BeautifulSoup
import re
import csv
import time

# -------- CONFIGURATION --------
BASE_URL = "https://www.thegamecornergames.com/collections/all"
OUTPUT_FILE = "game_corner_inventory.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def get_all_mtg_cards():
    results = []
    page = 1
    while True:
        url = f"{BASE_URL}?page={page}"
        print(f"Scraping page {page}...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            product_divs = soup.select('.productitem--info[data-available="true"]')

            if not product_divs:
                break  # No more products

            for product in product_divs:
                title_elem = product.select_one('.productitem--title')
                price_elem = product.select_one('.money')

                if title_elem and price_elem:
                    title = title_elem.get_text(strip=True)
                    price_text = price_elem.get_text()
                    found_prices = re.findall(r'\$?(\d+\.\d{2})', price_text)
                    if found_prices:
                        lowest_price = min(float(p) for p in found_prices)
                        results.append({"Card Name": title, "Price": lowest_price})

            page += 1
            time.sleep(1)  # be polite

        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    return results


def main():
    all_cards = get_all_mtg_cards()
    with open(OUTPUT_FILE, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Card Name", "Price"])
        writer.writeheader()
        writer.writerows(all_cards)

    print(f"Done. {len(all_cards)} cards saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
