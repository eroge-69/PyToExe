import pandas as pd
import re

# Pliki wejściowe
plik_txt = "x1.txt"
plik_xlsx = "x2.xlsx"
plik_wynik = "okazje.txt"

# 1. Wczytanie danych z x1.txt
with open(plik_txt, "r", encoding="utf-8") as f:
    dane_txt = f.read().splitlines()

# Słownik: {numer_zestawu: cały_wiersz_z_txt}
mapa_zestawow = {}
for linia in dane_txt:
    numer = linia.split("@")[0]
    mapa_zestawow[numer] = linia

# 2. Wczytanie danych z x2.xlsx (zakładamy, że dane są w pierwszym arkuszu)
df = pd.read_excel(plik_xlsx)

# 3. Kolumna A – wyszukiwanie numerów zestawów
#   Zakładamy, że numer to ciąg 4-7 cyfr w nazwie
wyniki = []
for _, row in df.iterrows():
    kolumna_a = str(row.iloc[0])  # kolumna A
    kolumna_h = str(row.iloc[7])  # kolumna H (8. kolumna, indeks 7)
    
    # Szukamy numeru zestawu w tekście kolumny A
    dopasowanie = re.search(r"\b\d{4,7}\b", kolumna_a)
    if dopasowanie:
        numer = dopasowanie.group()
        if numer in mapa_zestawow:
            # Dodajemy dane z x1.txt + '@' + wartość z kolumny H
            nowa_linia = mapa_zestawow[numer] + "@" + kolumna_h
            wyniki.append(nowa_linia)

# 4. Zapis do pliku wynikowego
with open(plik_wynik, "w", encoding="utf-8") as f:
    for linia in wyniki:
        f.write(linia + "\n")

print(f"Zapisano {len(wyniki)} wierszy do pliku {plik_wynik}.")
