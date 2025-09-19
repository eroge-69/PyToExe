import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Nagłówki HTTP
headers = {"User-Agent": "Mozilla/5.0"}

# URL główny
base_url = "https://www.morizon.pl/dzialki/pruszkowski/"

# Lista ofert
oferty_lista = []

def get_soup(url):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, "html.parser")

# Pobranie średniej ceny za m²
soup = get_soup(base_url)
srednia_text = soup.find("div", class_="statistic__value")
if srednia_text:
    try:
        srednia_cena_m2 = int(srednia_text.get_text(strip=True).replace(" ", "").replace("zł", ""))
    except:
        srednia_cena_m2 = 500
else:
    srednia_cena_m2 = 500

print(f"Średnia cena za m²: {srednia_cena_m2} zł")

# Funkcja przetwarzająca oferty
def przetworz_oferty(soup):
    oferty = soup.find_all("div", class_="listing__item")
    for oferta in oferty:
        try:
            cena_text = oferta.find("span", class_="listing__price").get_text(strip=True)
            powierzchnia_text = oferta.find("span", class_="listing__area").get_text(strip=True)
            link = oferta.find("a", href=True)["href"]

            cena = int(cena_text.replace(" ", "").replace("zł", ""))
            powierzchnia = int(powierzchnia_text.replace(" ", "").replace("m²", ""))
            cena_m2 = cena / powierzchnia

            if cena_m2 < 0.7 * srednia_cena_m2:
                oferty_lista.append({
                    "Link": link,
                    "Cena": cena,
                    "Powierzchnia": powierzchnia,
                    "Cena/m2": round(cena_m2, 2)
                })
        except:
            continue

# Paginacja - przechodzenie po stronach
strona = 1
while True:
    url = f"{base_url}?page={strona}"
    print(f"Pobieranie strony {strona}...")
    soup = get_soup(url)
    oferty_na_stronie = soup.find_all("div", class_="listing__item")
    if not oferty_na_stronie:
        break
    przetworz_oferty(soup)
    strona += 1
    time.sleep(1)

# Zapis wyników do CSV
df = pd.DataFrame(oferty_lista)
df.to_csv("tanie_oferty.csv", index=False, encoding="utf-8-sig")
print(f"Znaleziono {len(oferty_lista)} tanie oferty. Wynik zapisano do 'tanie_oferty.csv'.")
