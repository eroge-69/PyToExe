pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup
import time
import csv
import random
import os

def build_search_url(fn, ln, city='', province='', page=1):
    base = "https://www.canada411.ca/search/"
    params = f"?fn={fn}&ln={ln}"
    if city:
        params += f"&ct={city.replace(' ', '+')}"
    if province:
        params += f"&province={province.upper()}"
    params += f"&pg={page}"
    return base + params

def parse_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = soup.select('.listing')

    results = []
    for listing in listings:
        name = listing.select_one(".c411ListedName")
        phone = listing.select_one(".phones .phone")
        address = listing.select_one(".address")

        results.append([
            name.text.strip() if name else '',
            phone.text.strip() if phone else '',
            address.text.strip() if address else ''
        ])

    has_next = bool(soup.select_one('.pagination a:contains("Next")'))
    return results, has_next

def scrape_person(name, city, province):
    fn, *rest = name.split()
    ln = ' '.join(rest) if rest else ''
    page = 1
    all_results = []

    while True:
        url = build_search_url(fn, ln, city, province, page)
        print(f"Scraping: {url}")
        results, has_next = parse_page(url)
        all_results.extend(results)

        if not has_next:
            break
        page += 1
        time.sleep(random.uniform(1, 2))  # Rate limiting

    return all_results

def save_to_csv(data, filename="canada411_results.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Phone", "Address"])
        writer.writerows(data)

def main():
    print("📘 Canada411 Scraper (Python CLI Edition)")
    use_file = input("Use a .txt name list? (y/n): ").strip().lower() == 'y'

    names = []
    if use_file:
        path = input("Enter path to .txt file: ").strip()
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                names = [line.strip() for line in f if line.strip()]
        else:
            print("File not found.")
            return
    else:
        names.append(input("Enter name (First Last): ").strip())

    city_prov = input("Enter city,province (e.g., Toronto,ON): ").strip()
    if ',' in city_prov:
        city, province = city_prov.split(',')
    else:
        city, province = city_prov.strip(), ''

    all_results = []
    for name in names:
        results = scrape_person(name, city, province)
        all_results.extend(results)

    save_to_csv(all_results)
    print(f"✅ Done. Results saved to canada411_results.csv ({len(all_results)} listings)")

if __name__ == "__main__":
    main()
