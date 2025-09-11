import urllib.parse
import os

def wczytaj_stacje(plik):
    """Wczytuje wszystkie wpisy #SERVICE z pliku userbouquet"""
    with open(plik, "r", encoding="utf-8") as f:
        linie = f.readlines()

    stacje = []
    for linia in linie:
        if linia.startswith("#SERVICE"):
            stacje.append(linia.strip())
    return linie, stacje


def zapisz_nowa_kolejnosc(plik_wyj, linie, nowa_kolejnosc):
    """Zapisuje nową kolejność stacji do pliku wynikowego"""
    with open(plik_wyj, "w", encoding="utf-8") as f:
        # nadpisujemy nagłówek
        f.write("#NAME <((   R A D I O   ))>\n")

        # kopiujemy pozostałe linie poza starymi wpisami SERVICE/DESCRIPTION/NAME
        for linia in linie:
            if linia.startswith("#SERVICE") or linia.startswith("#DESCRIPTION") or linia.startswith("#NAME"):
                continue
            f.write(linia)
        # dopisujemy nowe wpisy
        for service, desc in nowa_kolejnosc:
            f.write(service + "\n")
            f.write(desc + "\n")


def znajdz_stacje_po_nazwie(stacje, nazwa):
    """Wyszukuje stację po fragmencie nazwy w istniejących wpisach"""
    for s in stacje:
        if nazwa.lower() in s.lower():
            return s
    return None


def zbuduj_service_entry(nazwa, url):
    """Buduje wpis #SERVICE i #DESCRIPTION dla nowej stacji"""
    url_enc = urllib.parse.quote(url, safe="")
    service_line = f"#SERVICE 1:0:2:0:0:0:0:0:0:0:{url_enc}:{nazwa}"
    description_line = f"#DESCRIPTION {nazwa}"
    return service_line, description_line


def main():
    plik = "userbouquet.polskie_stacje_radiowe_-_zet71.radio"
    lista_ulubionych = "moje_stacje.txt"
    plik_wyj = "userbouquet.dbe01.tv"   # nowa nazwa pliku wyjściowego

    if not os.path.exists(plik):
        print(f"❌ Nie znaleziono pliku: {plik}")
        return
    if not os.path.exists(lista_ulubionych):
        print(f"❌ Nie znaleziono pliku: {lista_ulubionych}")
        return

    # wczytaj oryginalny plik
    linie, stacje = wczytaj_stacje(plik)

    # wczytaj ulubione z pliku txt
    with open(lista_ulubionych, "r", encoding="utf-8") as f:
        ulubione_wpisy = [x.strip() for x in f if x.strip()]

    wybrane_stacje = []
    nowe_dodane = []

    for wpis in ulubione_wpisy:
        if "|" in wpis:  # nowa stacja: NAZWA|URL
            nazwa, url = wpis.split("|", 1)
            nazwa, url = nazwa.strip(), url.strip()
            service, desc = zbuduj_service_entry(nazwa, url)
            wybrane_stacje.append((service, desc))
            nowe_dodane.append(nazwa)
        else:  # istniejąca stacja z oryginalnego pliku
            stacja = znajdz_stacje_po_nazwie(stacje, wpis)
            if stacja:
                opis = f"#DESCRIPTION {wpis}"
                wybrane_stacje.append((stacja, opis))
            else:
                print(f"⚠️ Nie znaleziono w oryginale: {wpis}")

    # reszta stacji, które nie były wybrane
    pozostale = []
    for s in stacje:
        if any(s == ws[0] for ws in wybrane_stacje):
            continue
        opis = f"#DESCRIPTION {s.split(':')[-1]}"
        pozostale.append((s, opis))

    # finalna kolejność
    nowa_kolejnosc = wybrane_stacje + pozostale

    # zapisz do pliku
    zapisz_nowa_kolejnosc(plik_wyj, linie, nowa_kolejnosc)

    print("\n✅ Gotowe! Zapisano nową listę do:", plik_wyj)
    if nowe_dodane:
        print("➕ Dodano nowe stacje spoza oryginału:", ", ".join(nowe_dodane))


if __name__ == "__main__":
    main()
