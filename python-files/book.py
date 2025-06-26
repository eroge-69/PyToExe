import csv
import os
import time
from datetime import datetime, timedelta

# --- Definicje pól rekordu ---
FIELDS = ["Tytuł", "Autor", "Wydawnictwo", "Rok wydania", "Nr ISBN", "Cena"]

# --- Baza danych (lista rekordów) ---
baza = []

# --- Zmienna do liczenia czasu ---
start_time = time.time()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("="*48)
    print("         BAZA DANYCH KSIĄŻEK - WERSJA KONSOLOWA")
    print("="*48)

def read_file(filename):
    global baza
    try:
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            baza = [row for row in reader]
            print(f"\nWczytano bazę z pliku: {filename} ({len(baza)} rekordów)")
    except FileNotFoundError:
        print(f"\nPlik {filename} nie istnieje. Rozpoczynam z pustą bazą.")

def save_file(filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(baza)
    print(f"\nBaza zapisana do pliku: {filename}")

def input_field(prompt, allow_empty=False):
    while True:
        value = input(prompt)
        if value or allow_empty:
            return value.strip()

def add_record():
    record = []
    print("\nDodawanie nowej książki:")
    for f in FIELDS:
        val = input_field(f"  {f}: ")
        record.append(val)
    baza.append(record)
    print("\nDodano nowy rekord.")

def list_records(page_size=5):
    if not baza:
        print("\nBaza jest pusta.")
        return
    print(f"\nWyświetlanie wszystkich rekordów ({len(baza)}):")
    i = 0
    while i < len(baza):
        clear_screen()
        print_banner()
        for j in range(page_size):
            idx = i + j
            if idx >= len(baza): break
            rec = baza[idx]
            print(f"\n[{idx+1}] ", end='')
            for k, field in enumerate(FIELDS):
                print(f"{field}: {rec[k]}", end=' | ')
            print()
        print("\n(N)astępne, (P)oprzednie, (W)róć do menu")
        op = input("Wybierz: ").lower()
        if op == 'n':
            if i + page_size < len(baza):
                i += page_size
        elif op == 'p':
            if i - page_size >= 0:
                i -= page_size
        elif op == 'w':
            break

def list_single():
    if not baza:
        print("\nBaza jest pusta.")
        return
    idx = 0
    while True:
        clear_screen()
        print_banner()
        rec = baza[idx]
        print(f"\nRekord [{idx+1}/{len(baza)}]:")
        for k, field in enumerate(FIELDS):
            print(f"{field}: {rec[k]}")
        print("\n(N)astępny, (P)oprzedni, (W)róć do menu")
        op = input("Wybierz: ").lower()
        if op == 'n':
            idx = (idx + 1) % len(baza)
        elif op == 'p':
            idx = (idx - 1) % len(baza)
        elif op == 'w':
            break

def edit_record():
    if not baza:
        print("\nBaza jest pusta.")
        return
    list_all_short()
    try:
        num = int(input("Podaj numer rekordu do edycji: "))
        if not (1 <= num <= len(baza)):
            print("Niepoprawny numer!")
            return
        rec = baza[num-1]
        print("Podaj nowe wartości pól (Enter = bez zmian):")
        for i, field in enumerate(FIELDS):
            val = input_field(f"  {field} [{rec[i]}]: ", allow_empty=True)
            if val: rec[i] = val
        print("Rekord zaktualizowany.")
    except Exception:
        print("Błąd przy edycji rekordu!")

def delete_record():
    if not baza:
        print("\nBaza jest pusta.")
        return
    list_all_short()
    try:
        num = int(input("Podaj numer rekordu do usunięcia: "))
        if not (1 <= num <= len(baza)):
            print("Niepoprawny numer!")
            return
        confirm = input(f"Czy na pewno usunąć rekord {num}? (t/N): ").lower()
        if confirm == 't':
            del baza[num-1]
            print("Rekord usunięty.")
        else:
            print("Anulowano.")
    except Exception:
        print("Błąd przy usuwaniu rekordu!")

def sort_records():
    print("\nSortowanie bazy. Dostępne pola:")
    for i, field in enumerate(FIELDS):
        print(f"{i+1}. {field}")
    try:
        num = int(input("Wybierz pole do sortowania (numer): "))
        if not (1 <= num <= len(FIELDS)):
            print("Niepoprawny numer!")
            return
        baza.sort(key=lambda x: x[num-1].lower())
        print(f"Baza posortowana po polu: {FIELDS[num-1]}")
    except Exception:
        print("Błąd podczas sortowania.")

def show_time():
    t = int(time.time() - start_time)
    hh = t // 3600
    mm = (t % 3600) // 60
    ss = t % 60
    bar = "[" + "=" * (t//10) + ">" + " " * (30 - t//10) + "]"
    print("\nCzas spędzony w programie:")
    print(bar)
    print(f"{hh:02d}:{mm:02d}:{ss:02d}")

def list_all_short():
    print("\nRekordy w bazie:")
    for idx, rec in enumerate(baza):
        print(f"[{idx+1}] {rec[0]} | {rec[1]} | {rec[2]} | {rec[3]} | {rec[4]} | {rec[5]}")

def show_help():
    print("""
Dostępne funkcje i polecenia:
1 - Dodaj nowy rekord
2 - Przeglądaj rekordy (po stronach)
3 - Przeglądaj rekordy (pojedynczo)
4 - Edytuj wybrany rekord
5 - Usuń wybrany rekord
6 - Sortuj rekordy
7 - Wczytaj bazę z pliku
8 - Zapisz bazę do pliku
9 - Wyświetl czas pracy
10 - Pokaż pomoc
11 - Wiersz poleceń
12 - Wyjdź

Polecenia w wierszu poleceń:
  dodaj                  - dodaj nowy rekord
  przegladaj             - przeglądaj rekordy po stronach
  rekordy                - przeglądaj rekordy pojedynczo
  edytuj N               - edytuj rekord nr N
  usun N                 - usuń rekord nr N
  sortuj pole            - sortuj po polu: tytul/autor/wydawnictwo/rok/isbn/cena
  wczytaj plik.csv       - wczytaj bazę z pliku
  zapisz plik.csv        - zapisz bazę do pliku
  czas                   - pokaż czas pracy
  pomoc                  - wyświetl pomoc
  wyjdz                  - wyjście z wiersza poleceń
""")

def command_line():
    print("\nWiersz poleceń – wpisz 'pomoc' aby zobaczyć opcje.")
    while True:
        cmd = input(">> ").strip().lower()
        if cmd == "dodaj":
            add_record()
        elif cmd == "przegladaj":
            list_records()
        elif cmd == "rekordy":
            list_single()
        elif cmd.startswith("edytuj"):
            try:
                n = int(cmd.split()[1])
                if 1 <= n <= len(baza):
                    rec = baza[n-1]
                    print("Podaj nowe wartości pól (Enter = bez zmian):")
                    for i, field in enumerate(FIELDS):
                        val = input_field(f"  {field} [{rec[i]}]: ", allow_empty=True)
                        if val: rec[i] = val
                    print("Rekord zaktualizowany.")
                else:
                    print("Niepoprawny numer rekordu!")
            except:
                print("Użycie: edytuj N")
        elif cmd.startswith("usun"):
            try:
                n = int(cmd.split()[1])
                if 1 <= n <= len(baza):
                    confirm = input(f"Czy na pewno usunąć rekord {n}? (t/N): ").lower()
                    if confirm == 't':
                        del baza[n-1]
                        print("Rekord usunięty.")
                    else:
                        print("Anulowano.")
                else:
                    print("Niepoprawny numer rekordu!")
            except:
                print("Użycie: usun N")
        elif cmd.startswith("sortuj"):
            try:
                pole = cmd.split()[1]
                fields_map = {
                    "tytul": 0, "autor": 1, "wydawnictwo": 2, "rok": 3, "isbn": 4, "cena": 5
                }
                if pole in fields_map:
                    baza.sort(key=lambda x: x[fields_map[pole]].lower())
                    print(f"Baza posortowana po polu: {FIELDS[fields_map[pole]]}")
                else:
                    print("Nieznane pole!")
            except:
                print("Użycie: sortuj tytul|autor|wydawnictwo|rok|isbn|cena")
        elif cmd.startswith("wczytaj"):
            try:
                filename = cmd.split()[1]
                read_file(filename)
            except:
                print("Użycie: wczytaj plik.csv")
        elif cmd.startswith("zapisz"):
            try:
                filename = cmd.split()[1]
                save_file(filename)
            except:
                print("Użycie: zapisz plik.csv")
        elif cmd == "czas":
            show_time()
        elif cmd == "pomoc":
            show_help()
        elif cmd == "wyjdz":
            print("Wyjście z wiersza poleceń.")
            break
        else:
            print("Nieznane polecenie. Wpisz 'pomoc'.")

def main_menu():
    last_file = "books.csv"
    while True:
        clear_screen()
        print_banner()
        print("""
1. Dodaj nowy rekord
2. Przeglądaj rekordy (po stronach)
3. Przeglądaj rekordy (pojedynczo)
4. Edytuj wybrany rekord
5. Usuń wybrany rekord
6. Sortuj rekordy
7. Wczytaj bazę z pliku
8. Zapisz bazę do pliku
9. Wyświetl czas pracy
10. Pokaż pomoc
11. Wiersz poleceń
12. Wyjdź
""")
        choice = input("Wybierz opcję (1-12): ").strip()
        if choice == '1':
            add_record()
            input("\nEnter aby kontynuować...")
        elif choice == '2':
            list_records()
        elif choice == '3':
            list_single()
        elif choice == '4':
            edit_record()
            input("\nEnter aby kontynuować...")
        elif choice == '5':
            delete_record()
            input("\nEnter aby kontynuować...")
        elif choice == '6':
            sort_records()
            input("\nEnter aby kontynuować...")
        elif choice == '7':
            filename = input("Podaj nazwę pliku do wczytania (domyślnie books.csv): ").strip() or last_file
            read_file(filename)
            last_file = filename
            input("\nEnter aby kontynuować...")
        elif choice == '8':
            filename = input("Podaj nazwę pliku do zapisu (domyślnie books.csv): ").strip() or last_file
            save_file(filename)
            last_file = filename
            input("\nEnter aby kontynuować...")
        elif choice == '9':
            show_time()
            input("\nEnter aby kontynuować...")
        elif choice == '10':
            show_help()
            input("\nEnter aby kontynuować...")
        elif choice == '11':
            command_line()
        elif choice == '12':
            clear_screen()
            print_banner()
            show_time()
            print("\nDziękujemy za korzystanie z programu!")
            break
        else:
            print("Niepoprawna opcja!")
            input("Enter aby kontynuować...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        clear_screen()
        print_banner()
        show_time()
        print("\nProgram przerwany przez użytkownika. Do zobaczenia!\n")
