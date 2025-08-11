import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib.parse

def scrape_google_maps(niche, location):
    query = f"{niche} {location} site:maps.google.com"
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&num=50"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
    print(f"[INFO] Searching Google Maps for: {niche} in {location}")
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for g in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd'):
        name = g.get_text()
        parent = g.find_parent()
        snippet = parent.get_text(" ", strip=True) if parent else ""
        phones = re.findall(r'\+?\d[\d\s\-\(\)]{7,}\d', snippet)
        emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', snippet)
        results.append({
            "Source": "Google Maps",
            "Name": name,
            "Details": snippet,
            "Phones": ", ".join(set(phones)),
            "Emails": ", ".join(set(emails))
        })
    return results

def scrape_yellow_pages(niche, location):
    base_url = f"https://www.yellowpages.com/search?search_terms={urllib.parse.quote(niche)}&geo_location_terms={urllib.parse.quote(location)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    }
    print(f"[INFO] Searching Yellow Pages for: {niche} in {location}")
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    for listing in soup.find_all('div', class_='result'):
        name_tag = listing.find('a', class_='business-name')
        name = name_tag.get_text(strip=True) if name_tag else ""
        phone_tag = listing.find('div', class_='phones phone primary')
        phone = phone_tag.get_text(strip=True) if phone_tag else ""
        email = ""  # Yellow Pages usually hides emails
        results.append({
            "Source": "Yellow Pages",
            "Name": name,
            "Details": "",
            "Phones": phone,
            "Emails": email
        })
    return results

if _name_ == "_main_":
    niche_input = input("Enter niche: ")
    location_input = input("Enter location: ")

    all_results = []
    all_results.extend(scrape_google_maps(niche_input, location_input))
    all_results.extend(scrape_yellow_pages(niche_input, location_input))

    df = pd.DataFrame(all_results)
    file_name = f"{niche_input}{location_input}_leads.csv".replace(" ", "")
    df.to_csv(file_name, index=False, encoding='utf-8-sig')
    print(f"[INFO] Saved {len(df)} results to {file_name}")