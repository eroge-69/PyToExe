import os

def wczytaj_dane_z_pliku(nazwa_pliku):
    dane = {}
    if not os.path.exists(nazwa_pliku):
        print(f"Błąd: Plik '{nazwa_pliku}' nie został znaleziony.")
        return dane

    with open(nazwa_pliku, 'r', encoding='utf-8') as plik:
        for linia in plik:
            linia = linia.strip()
            if '@' in linia:
                numer, opis = linia.split('@', 1)
                dane[numer.strip()] = opis.strip()
    return dane

def main():
    nazwa_pliku = "1x.txt"
    dane_produktow = wczytaj_dane_z_pliku(nazwa_pliku)

    if not dane_produktow:
        print("Brak danych do przeszukania. Zakończono.")
        return

    print("=== Wyszukiwarka produktów ===")
    print("Wpisz numer produktu i naciśnij Enter (lub wpisz 'exit' aby zakończyć):")

    while True:
        numer = input("Numer produktu: ").strip()
        if numer.lower() == 'exit':
            print("Zakończono działanie programu.")
            break
        elif numer in dane_produktow:
            print(f"Dane produktu dla {numer}:")
            print(dane_produktow[numer])
        else:
            print(f"Nie znaleziono danych dla produktu o numerze: {numer}")

if __name__ == "__main__":
    main()
