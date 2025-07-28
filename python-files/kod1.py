#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYSTEM MAGAZYNOWY
=================
Program do zarzÄ…dzania magazynem z funkcjami:
- Przyjmowanie towarÃ³w z okreÅ›lonÄ… cenÄ…
- Obliczanie zysku i marÅ¼y na podstawie narzutu %
- ÅšciÄ…ganie towaru z magazynu o okreÅ›lonej cenie
- Eksport danych do CSV

Autor: System AI
Data: 2025-07-29
"""

import json
import datetime
from typing import Dict, List, Optional
import csv

class Towar:
    def __init__(self, id_towaru: str, nazwa: str, cena_zakupu: float, ilosc: int = 0):
        self.id_towaru = id_towaru
        self.nazwa = nazwa
        self.cena_zakupu = cena_zakupu
        self.ilosc = ilosc
        self.data_dodania = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            'id_towaru': self.id_towaru,
            'nazwa': self.nazwa,
            'cena_zakupu': self.cena_zakupu,
            'ilosc': self.ilosc,
            'data_dodania': self.data_dodania
        }

class Magazyn:
    def __init__(self):
        self.towary: Dict[str, Towar] = {}
        self.historia_operacji: List[Dict] = []

    def przyjmij_towar(self, id_towaru: str, nazwa: str, cena_zakupu: float, ilosc: int) -> str:
        """Przyjmuje towar do magazynu"""
        if id_towaru in self.towary:
            # JeÅ›li towar juÅ¼ istnieje, aktualizuj iloÅ›Ä‡ i cenÄ™ (Å›rednia waÅ¼ona)
            stary_towar = self.towary[id_towaru]
            nowa_ilosc = stary_towar.ilosc + ilosc

            # Oblicz Å›redniÄ… waÅ¼onÄ… cenÄ™ zakupu
            if nowa_ilosc > 0:
                nowa_cena = ((stary_towar.cena_zakupu * stary_towar.ilosc) + 
                           (cena_zakupu * ilosc)) / nowa_ilosc
                stary_towar.cena_zakupu = round(nowa_cena, 2)

            stary_towar.ilosc = nowa_ilosc
            komunikat = f"Zaktualizowano towar {nazwa}. Nowa iloÅ›Ä‡: {nowa_ilosc}, Nowa Å›rednia cena: {stary_towar.cena_zakupu:.2f} PLN"
        else:
            # Dodaj nowy towar
            self.towary[id_towaru] = Towar(id_towaru, nazwa, cena_zakupu, ilosc)
            komunikat = f"Dodano nowy towar {nazwa}. IloÅ›Ä‡: {ilosc}, Cena zakupu: {cena_zakupu:.2f} PLN"

        # Zapisz operacjÄ™ do historii
        self.historia_operacji.append({
            'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'operacja': 'PRZYJÄ˜CIE',
            'id_towaru': id_towaru,
            'nazwa': nazwa,
            'ilosc': ilosc,
            'cena': cena_zakupu,
            'wartosc': ilosc * cena_zakupu
        })

        return komunikat

    def wydaj_towar(self, id_towaru: str, ilosc: int, cena_sprzedazy: float) -> str:
        """Wydaje towar z magazynu i oblicza zysk"""
        if id_towaru not in self.towary:
            return f"BÅ‚Ä…d: Towar o ID {id_towaru} nie istnieje w magazynie"

        towar = self.towary[id_towaru]

        if towar.ilosc < ilosc:
            return f"BÅ‚Ä…d: NiewystarczajÄ…ca iloÅ›Ä‡ towaru. DostÄ™pne: {towar.ilosc}, Å¼Ä…dane: {ilosc}"

        # Oblicz zysk i marÅ¼Ä™
        koszt_calkowity = towar.cena_zakupu * ilosc
        przychod = cena_sprzedazy * ilosc
        zysk = przychod - koszt_calkowity
        marza_procent = (zysk / przychod * 100) if przychod > 0 else 0
        narzut_procent = (zysk / koszt_calkowity * 100) if koszt_calkowity > 0 else 0

        # Aktualizuj stan magazynu
        towar.ilosc -= ilosc

        # Zapisz operacjÄ™ do historii
        self.historia_operacji.append({
            'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'operacja': 'WYDANIE',
            'id_towaru': id_towaru,
            'nazwa': towar.nazwa,
            'ilosc': ilosc,
            'cena_zakupu': towar.cena_zakupu,
            'cena_sprzedazy': cena_sprzedazy,
            'koszt_calkowity': koszt_calkowity,
            'przychod': przychod,
            'zysk': zysk,
            'marza_procent': round(marza_procent, 2),
            'narzut_procent': round(narzut_procent, 2)
        })

        komunikat = f"""
Wydano towar: {towar.nazwa}
IloÅ›Ä‡: {ilosc}
Cena zakupu jednostkowa: {towar.cena_zakupu:.2f} PLN
Cena sprzedaÅ¼y jednostkowa: {cena_sprzedazy:.2f} PLN
Koszt caÅ‚kowity: {koszt_calkowity:.2f} PLN
PrzychÃ³d: {przychod:.2f} PLN
Zysk: {zysk:.2f} PLN
MarÅ¼a: {marza_procent:.2f}%
Narzut: {narzut_procent:.2f}%
PozostaÅ‚a iloÅ›Ä‡ w magazynie: {towar.ilosc}
        """

        return komunikat.strip()

    def oblicz_marze_z_narzutu(self, cena_zakupu: float, narzut_procent: float) -> Dict:
        """Oblicza cenÄ™ sprzedaÅ¼y i marÅ¼Ä™ na podstawie narzutu"""
        cena_sprzedazy = cena_zakupu * (1 + narzut_procent / 100)
        zysk = cena_sprzedazy - cena_zakupu
        marza_procent = (zysk / cena_sprzedazy) * 100

        return {
            'cena_zakupu': round(cena_zakupu, 2),
            'narzut_procent': narzut_procent,
            'cena_sprzedazy': round(cena_sprzedazy, 2),
            'zysk_jednostkowy': round(zysk, 2),
            'marza_procent': round(marza_procent, 2)
        }

    def pokaz_stan_magazynu(self) -> str:
        """Pokazuje aktualny stan magazynu"""
        if not self.towary:
            return "Magazyn jest pusty"

        wynik = "STAN MAGAZYNU:\n" + "="*50 + "\n"
        wartosc_calkowita = 0

        for towar in self.towary.values():
            wartosc_towaru = towar.ilosc * towar.cena_zakupu
            wartosc_calkowita += wartosc_towaru
            wynik += f"ID: {towar.id_towaru}\n"
            wynik += f"Nazwa: {towar.nazwa}\n"
            wynik += f"IloÅ›Ä‡: {towar.ilosc}\n"
            wynik += f"Cena zakupu: {towar.cena_zakupu:.2f} PLN\n"
            wynik += f"WartoÅ›Ä‡: {wartosc_towaru:.2f} PLN\n"
            wynik += f"Data dodania: {towar.data_dodania}\n"
            wynik += "-" * 30 + "\n"

        wynik += f"CAÅKOWITA WARTOÅšÄ† MAGAZYNU: {wartosc_calkowita:.2f} PLN"
        return wynik

    def eksportuj_do_csv(self, nazwa_pliku: str = "stan_magazynu.csv"):
        """Eksportuje stan magazynu do pliku CSV"""
        with open(nazwa_pliku, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id_towaru', 'nazwa', 'ilosc', 'cena_zakupu', 'wartosc', 'data_dodania']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for towar in self.towary.values():
                writer.writerow({
                    'id_towaru': towar.id_towaru,
                    'nazwa': towar.nazwa,
                    'ilosc': towar.ilosc,
                    'cena_zakupu': towar.cena_zakupu,
                    'wartosc': towar.ilosc * towar.cena_zakupu,
                    'data_dodania': towar.data_dodania
                })

    def eksportuj_historie_do_csv(self, nazwa_pliku: str = "historia_operacji.csv"):
        """Eksportuje historiÄ™ operacji do pliku CSV"""
        if not self.historia_operacji:
            return "Brak operacji do eksportu"

        # Zbierz wszystkie moÅ¼liwe klucze z wszystkich operacji
        wszystkie_klucze = set()
        for operacja in self.historia_operacji:
            wszystkie_klucze.update(operacja.keys())

        # Sortuj klucze dla lepszej czytelnoÅ›ci
        fieldnames = sorted(list(wszystkie_klucze))

        with open(nazwa_pliku, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for operacja in self.historia_operacji:
                # UzupeÅ‚nij brakujÄ…ce klucze pustymi wartoÅ›ciami
                row = {klucz: operacja.get(klucz, '') for klucz in fieldnames}
                writer.writerow(row)

def menu_glowne():
    """GÅ‚Ã³wne menu programu"""
    magazyn = Magazyn()

    while True:
        print("\n" + "="*50)
        print("           SYSTEM MAGAZYNOWY")
        print("="*50)
        print("1. Przyjmij towar")
        print("2. Wydaj towar")
        print("3. PokaÅ¼ stan magazynu")
        print("4. Oblicz marÅ¼Ä™ z narzutu")
        print("5. Eksportuj stan magazynu do CSV")
        print("6. Eksportuj historiÄ™ operacji do CSV")
        print("0. WyjÅ›cie")
        print("="*50)

        wybor = input("Wybierz opcjÄ™ (0-6): ").strip()

        if wybor == "1":
            try:
                id_towaru = input("Podaj ID towaru: ").strip()
                nazwa = input("Podaj nazwÄ™ towaru: ").strip()
                cena_zakupu = float(input("Podaj cenÄ™ zakupu: "))
                ilosc = int(input("Podaj iloÅ›Ä‡: "))

                if cena_zakupu < 0 or ilosc < 0:
                    print("BÅ‚Ä…d: Cena i iloÅ›Ä‡ muszÄ… byÄ‡ dodatnie!")
                    continue

                wynik = magazyn.przyjmij_towar(id_towaru, nazwa, cena_zakupu, ilosc)
                print(f"\nâœ… {wynik}")

            except ValueError:
                print("\nâŒ BÅ‚Ä…d: NieprawidÅ‚owe dane! SprawdÅº format liczb.")

        elif wybor == "2":
            try:
                id_towaru = input("Podaj ID towaru do wydania: ").strip()
                ilosc = int(input("Podaj iloÅ›Ä‡ do wydania: "))
                cena_sprzedazy = float(input("Podaj cenÄ™ sprzedaÅ¼y: "))

                if ilosc <= 0 or cena_sprzedazy < 0:
                    print("BÅ‚Ä…d: IloÅ›Ä‡ musi byÄ‡ dodatnia, cena nie moÅ¼e byÄ‡ ujemna!")
                    continue

                wynik = magazyn.wydaj_towar(id_towaru, ilosc, cena_sprzedazy)
                print(f"\n{wynik}")

            except ValueError:
                print("\nâŒ BÅ‚Ä…d: NieprawidÅ‚owe dane! SprawdÅº format liczb.")

        elif wybor == "3":
            print("\n" + magazyn.pokaz_stan_magazynu())

        elif wybor == "4":
            try:
                cena_zakupu = float(input("Podaj cenÄ™ zakupu: "))
                narzut = float(input("Podaj narzut w % (np. 25 dla 25%): "))

                wynik = magazyn.oblicz_marze_z_narzutu(cena_zakupu, narzut)
                print(f"\nðŸ“Š KALKULATOR MARÅ»Y:")
                print(f"Cena zakupu: {wynik['cena_zakupu']} PLN")
                print(f"Narzut: {wynik['narzut_procent']}%")
                print(f"Cena sprzedaÅ¼y: {wynik['cena_sprzedazy']} PLN")
                print(f"Zysk jednostkowy: {wynik['zysk_jednostkowy']} PLN")
                print(f"MarÅ¼a: {wynik['marza_procent']}%")

            except ValueError:
                print("\nâŒ BÅ‚Ä…d: NieprawidÅ‚owe dane! SprawdÅº format liczb.")

        elif wybor == "5":
            nazwa_pliku = input("Podaj nazwÄ™ pliku CSV (lub Enter dla domyÅ›lnej): ").strip()
            if not nazwa_pliku:
                nazwa_pliku = "stan_magazynu.csv"

            magazyn.eksportuj_do_csv(nazwa_pliku)
            print(f"\nâœ… Eksportowano stan magazynu do pliku: {nazwa_pliku}")

        elif wybor == "6":
            nazwa_pliku = input("Podaj nazwÄ™ pliku CSV (lub Enter dla domyÅ›lnej): ").strip()
            if not nazwa_pliku:
                nazwa_pliku = "historia_operacji.csv"

            wynik = magazyn.eksportuj_historie_do_csv(nazwa_pliku)
            if wynik:
                print(f"\nâš ï¸ {wynik}")
            else:
                print(f"\nâœ… Eksportowano historiÄ™ operacji do pliku: {nazwa_pliku}")

        elif wybor == "0":
            print("\nðŸ‘‹ DziÄ™kujemy za korzystanie z systemu magazynowego!")
            break
        else:
            print("\nâŒ NieprawidÅ‚owy wybÃ³r! Wybierz opcjÄ™ 0-6.")

if __name__ == "__main__":
    menu_glowne()