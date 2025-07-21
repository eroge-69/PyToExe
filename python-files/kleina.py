import requests
from bs4 import BeautifulSoup
import time
import re
import os

# === KONFIGURACJA ===
PLIK_ZESTAWY = 'x1.txt'
PLIK_OFEROWANE = 'oferty_zapamietane.txt'
PLIK_LOG = 'oferty.txt'
INTERWAL_CZASOWY = 300  # 5 minut
OPÓŹNIENIE_MIEDZY_STRONAMI = 5  # sekundy
MAX_STRON = 50

# === WCZYTYWANIE ZESTAWÓW ===
def wczytaj_zestawy(plik):
    zestawy = []
    with open(plik, 'r', encoding='utf-8') as f:
        for linia in f:
            czesci = linia.strip().split('@')
            if len(czesci) == 4:
                numer, min_cena, max_cena, nazwa = czesci
                zestawy.append({
                    'numer': numer,
                    'min': float(min_cena),
                    'max': float(max_cena),
                    'nazwa': nazwa
                })
    return zestawy

# === WCZYTYWANIE LINKÓW JUŻ PRZETWORZONYCH ===
def wczytaj_zapamietane():
    if not os.path.exists(PLIK_OFEROWANE):
        return set()
    with open(PLIK_OFEROWANE, 'r', encoding='utf-8') as f:
        return set(linia.strip() for linia in f if linia.strip())

def zapisz_link(link):
    with open(PLIK_OFEROWANE, 'a', encoding='utf-8') as f:
        f.write(link + '\n')

def zapisz_oferte(tresc):
    with open(PLIK_LOG, 'a', encoding='utf-8') as f:
        f.write(tresc + '\n')

# === SPRAWDZANIE OFERT ===
def sprawdz_oferty(zestawy, zapamietane_linki):
    baza_url = "https://www.kleinanzeigen.de/s-spielzeug/lego/k0c23+spielzeug.condition_s:new"
    headers = {"User-Agent": "Mozilla/5.0"}

    for page in range(1, MAX_STRON + 1):
        url = f"{baza_url}/seite:{page}"
        print(f"Sprawdzam stronę: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            oferty = soup.find_all('article')

            if not oferty:
                break  # koniec wyników

            for oferta in oferty:
                tytul_tag = oferta.find('a', class_='ellipsis')
                cena_tag = oferta.find('p', class_='aditem-main--middle--price-shipping--price')
                link_tag = oferta.find('a', href=True)

                if not tytul_tag or not cena_tag or not link_tag:
                    continue

                tytul = tytul_tag.text.strip()
                cena_str = cena_tag.text.strip()
                link = "https://www.kleinanzeigen.de" + link_tag['href'].split('?')[0]

                # pomiń jeśli już zapamiętane
                if link in zapamietane_linki:
                    continue

                # pomiń jeśli w tytule więcej niż jeden numer zestawu
                numery_w_tytule = re.findall(r'\b\d{4,5}\b', tytul)
                if len(numery_w_tytule) != 1:
                    continue

                # wyciągnięcie ceny
                cena_match = re.search(r'(\d+(?:[.,]\d+)?)\s*€', cena_str)
                if not cena_match:
                    continue
                cena = float(cena_match.group(1).replace(',', '.'))

                for zestaw in zestawy:
                    if zestaw['numer'] in tytul and "LEGO" in tytul.upper():
                        if zestaw['min'] <= cena <= zestaw['max']:
                            tresc = f"LEGO {zestaw['numer']}___{int(cena)}e___{zestaw['nazwa']}\n{link}"
                            print(tresc)
                            zapisz_oferte(tresc)
                            zapisz_link(link)
                            zapamietane_linki.add(link)
            time.sleep(OPÓŹNIENIE_MIEDZY_STRONAMI)

        except Exception as e:
            print("Błąd:", e)
            break

# === GŁÓWNA PĘTLA ===
def main():
    zestawy = wczytaj_zestawy(PLIK_ZESTAWY)
    zapamietane_linki = wczytaj_zapamietane()
    print("Sprawdzam ceny na Kleinanzeigen.de")

    while True:
        sprawdz_oferty(zestawy, zapamietane_linki)
        time.sleep(INTERWAL_CZASOWY)

if __name__ == "__main__":
    main()
