import os
import sys

def wypełnij_szablon(sciezka_szablonu, dane):
    """Podmienia placeholdery w szablonie HTML na dane"""
    if not os.path.isfile(sciezka_szablonu):
        print(f"Błąd: brak szablonu {sciezka_szablonu}")
        sys.exit(1)
    with open(sciezka_szablonu, 'r', encoding='utf-8') as f:
        szablon = f.read()
    for klucz, wartosc in dane.items():
        szablon = szablon.replace(f"{{{{{klucz}}}}}", wartosc)
    return szablon

# Folder, w którym jest skrypt (i szablony)
folder = os.path.dirname(os.path.abspath(__file__))

# Pytamy ile będzie zastępców
while True:
    try:
        liczba_zastepcow = int(input("Ile będzie zastępców (1-3)? "))
        if liczba_zastepcow in [1,2,3]:
            break
        else:
            print("Proszę podać liczbę 1, 2 lub 3.")
    except ValueError:
        print("Proszę podać poprawną liczbę.")

# Dane osoby nieobecnej
dane = {}
dane["IMIE_NAZWISKO"] = input("Podaj imię i nazwisko osoby nieobecnej: ")
dane["DATA_OD"] = input("Podaj datę rozpoczęcia urlopu (np. 22.09.2025): ")
dane["DATA_DO"] = input("Podaj datę zakończenia urlopu (np. 03.10.2025): ")

# Dane zastępców
for i in range(1, liczba_zastepcow + 1):
    print(f"\n--- Zastępca {i} ---")
    dane[f"ZASTEPCA{i}"] = input(f"Podaj imię i nazwisko zastępcy {i}: ")
    dane[f"TELEFON_ZASTEPCA{i}"] = input(f"Podaj numer telefonu zastępcy {i} (np. +48603266737): ")
    dane[f"EMAIL_ZASTEPCA{i}"] = input(f"Podaj adres e-mail zastępcy {i} (np. przyklad@domena.pl): ")

# Wybór szablonu w zależności od liczby zastępców
sciezka_szablonu = os.path.join(folder, f"autoresponder-{liczba_zastepcow}.html")

# Wypełnianie szablonu
gotowy_html = wypełnij_szablon(sciezka_szablonu, dane)

# Tworzymy nazwę pliku: imie_nazwisko_dataod.html
imie_nazwisko_clean = dane["IMIE_NAZWISKO"].replace(" ", "_")
data_od_clean = dane["DATA_OD"].replace(".", "-")
wyjscie = os.path.join(folder, f"{imie_nazwisko_clean}_{data_od_clean}.html")

# Zapis do pliku
with open(wyjscie, 'w', encoding='utf-8') as f:
    f.write(gotowy_html)

print(f"\nGotowy plik zapisany jako {wyjscie}")
print("Możesz teraz zamknąć program.")
