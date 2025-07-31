from dataclasses import dataclass
import json
import re
import sys, os
import unicodedata
import pandas as pd
import csv
import openpyxl
import requests
from bs4 import BeautifulSoup
from datetime import datetime

API_URL = "https://graphql-prod-4777.prod.aws.worldathletics.org/graphql"
HEADERS = {
    "x-api-key": "da2-b5clb5uvrjehfpublcwaz74mg4",
    "Content-Type": "application/json",
    "Origin": "https://worldathletics.org",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}

# Mapowanie lat na format URL
OLYMPIC_GAMES = {
    "2024": "paris-2024",
    "2021": "tokyo-2020",  # Faktycznie odbyły się w 2021
    "2016": "rio-2016",
    "2012": "london-2012",
    "2008": "beijing-2008",
    "2004": "athens-2004",
    "2000": "sydney-2000",
    "1996": "atlanta-1996",
    "1992": "barcelona-1992",
    "1988": "seoul-1988",
    "1984": "los-angeles-1984",
    "1980": "moscow-1980",
    "1976": "montreal-1976",
    "1972": "monachium-1972",
    "1968": "mexico-city-1968",
    "1964": "tokyo-1964",
    "1960": "rome-1960",
    "1956": "melbourne-1956",
    "1952": "helsinki-1952",
    "1948": "london-1948",
    "1936": "berlin-1936",
    "1932": "los-angeles-1932",
    "1928": "amsterdam-1928",
    "1924": "paris-1924",
    "1920": "antwerp-1920",
    "1912": "stockholm-1912",
    "1908": "london-1908",
    "1904": "st-louis-1904",
    "1900": "paris-1900",
    "1896": "athens-1896",
}
    
DISCIPLINE_MAP = {
    "100M": "100m",
    "200M": "200m",
    "400M": "400m",
    "400MH": "400m-hurdles",
    "100MH": "100m-hurdles",
    "110MH": "110m-hurdles",
    "800M": "800m",
    "1500M": "1500m",
    "LJ": "long-jump",
    "HJ": "high-jump",
}

def find_athlete_id(name):
    query = """
    query SearchCompetitors($query: String) {
      searchCompetitors(query: $query) {
        aaAthleteId
        familyName
        givenName
      }
    }
    """
    variables = {"query": name}
    response = requests.post(API_URL, json={
        "operationName": "SearchCompetitors",
        "query": query,
        "variables": variables
    }, headers=HEADERS)
    data = response.json()
    athletes = data.get("data", {}).get("searchCompetitors", [])
    if not athletes:
        raise ValueError(f"Nie znaleziono zawodnika o nazwie: {name}")
    return athletes[0]["aaAthleteId"]

def get_athlete_results(athlete_id, season):
    query = """
    query GetSingleCompetitorResultsDate($id: Int, $resultsByYear: Int, $resultsByYearOrderBy: String) {
      getSingleCompetitorResultsDate(id: $id, resultsByYear: $resultsByYear, resultsByYearOrderBy: $resultsByYearOrderBy) {
        resultsByDate {
          date
          competition
          venue
          discipline
          place
          mark
          wind
          resultScore
          remark
        }
      }
    }
    """
    variables = {
        "id": athlete_id,
        "resultsByYear": int(season),
        "resultsByYearOrderBy": "date"
    }
    response = requests.post(API_URL, json={
        "operationName": "GetSingleCompetitorResultsDate",
        "query": query,
        "variables": variables
    }, headers=HEADERS)
    data = response.json()
    results = data.get("data", {}).get("getSingleCompetitorResultsDate", {}).get("resultsByDate", [])
    if not results:
        raise ValueError(f"Brak wyników dla zawodnika ID={athlete_id} w sezonie {season}")

    formatted_results = []
    for r in results:
        try:
            dt = datetime.strptime(r["date"], "%d %b %Y")
            date_str = dt.strftime("%d.%m.%Y")
        except Exception:
            date_str = r["date"]
        
        formatted_results.append({
            "Data": date_str,
            "Zawody": r.get("competition", ""),
            "Konkurencja": r.get("discipline", ""),
            "Wynik": r.get("mark", ""),
            "Punkty": r.get("resultScore", ""),
        })

    return pd.DataFrame(formatted_results)

def get_personal_best(athlete_id, discipline):
    """Pobiera rekord życiowy - pierwszy wynik z listy jest najlepszy"""
    query = """
    query GetTopResults($id: Int!) {
      getSingleCompetitorAllTimePersonalTop10(id: $id) {
        results {
          discipline
          result
          date
          competition
          records
        }
      }
    }
    """
    
    try:
        response = requests.post(
            API_URL,
            json={
                "operationName": "GetTopResults",
                "query": query,
                "variables": {"id": int(athlete_id)}
            },
            headers=HEADERS,
            timeout=10
        )
        
        data = response.json()
        
        # Pobierz wszystkie wyniki
        all_results = data.get("data", {}).get("getSingleCompetitorAllTimePersonalTop10", {}).get("results", [])
        
        if not all_results:
            raise ValueError("Brak wyników w odpowiedzi API")
            
        # Filtruj tylko wyniki dla żądanej dyscypliny
        discipline_results = [
            r for r in all_results 
            if r.get("discipline", "").upper() == discipline.upper()
        ]
        
        if not discipline_results:
            available = {r["discipline"] for r in all_results if r.get("discipline")}
            raise ValueError(f"Brak wyników dla '{discipline}'. Dostępne: {', '.join(available)}")
        
        # Pierwszy wynik jest rekordem życiowym
        pb = discipline_results[0]
        
        return {
            "Discipline": pb["discipline"],
            "Result": pb["result"],
            "Date": pb["date"],
            "Competition": pb["competition"],
            "Records": pb.get("records", []),
        }
        
    except Exception as e:
        raise ValueError(f"Błąd API: {str(e)}")

def save_personal_bests_to_file(athletes, discipline, filename):
    """Zapisuje rekordy życiowe do pliku CSV z polskim formatem liczb"""
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        
        # Nagłówki kolumn
        writer.writerow([
            "Zawodnik", 
            "Dyscyplina", 
            "Rekord życiowy", 
            "Data", 
            "Zawody", 
            "Typ rekordu"
        ])
        
        for athlete in athletes:
            try:
                # Zamiana kropek na przecinki w wyniku
                result = athlete['Result'].replace('.', ',')
                
                # Formatowanie rekordu
                record_type = ', '.join(athlete['Records']) if athlete['Records'] else '-'
                
                # Formatowanie daty (jeśli potrzebne)
                try:
                    date_obj = datetime.strptime(athlete['Date'], "%d %b %Y")
                    formatted_date = date_obj.strftime("%d.%m.%Y")
                except:
                    formatted_date = athlete['Date']
                
                writer.writerow([
                    athlete['Name'],
                    discipline,
                    formatted_date,
                    athlete['Competition'],
                    result,
                    record_type
                ])
                
            except Exception as e:
                print(f"Błąd przy zapisie dla {athlete.get('Name', '?')}: {str(e)}")
    
    print(f"\n✅ Zapisano wyniki do pliku {filename}")

def get_input_source():
    """Pyta użytkownika o źródło danych"""
    print("\nWybierz źródło danych:")
    print("1 - Wprowadź ręcznie (imiona i nazwiska oddzielone przecinkami)")
    print("2 - Wczytaj z pliku (nazwy zawodników w osobnych liniach)")
    while True:
        choice = input("Twój wybór (1/2): ").strip()
        if choice in ('1', '2'):
            return choice
        print("Proszę wybrać 1 lub 2")

def save_to_same_file(athletes_data, original_filename, discipline):
    """Zapisuje rekordy życiowe do istniejącego pliku, zachowując kolumnę A"""
    try:
        # Odczytaj oryginalne dane
        with open(original_filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            original_rows = list(reader)
        
        # Przygotuj nowe dane
        new_rows = []
        for i, row in enumerate(original_rows):
            if i % 9 == 0:  # Linie z nazwiskami zawodników
                name = row[0].strip()
                if name and name != "Data":
                    # Znajdź rekord dla tego zawodnika
                    pb = next((a for a in athletes_data if a['Name'] == name), None)
                    if pb:
                        # Formatowanie daty na dd.mm.yyyy
                        try:
                            date_obj = datetime.strptime(pb['Date'], "%d %b %Y")
                            formatted_date = date_obj.strftime("%d.%m.%Y")
                        except:
                            formatted_date = pb['Date']  # Jeśli format nieznany, zostaw oryginał
                        # Zachowaj kolumnę A, dodaj nowe dane
                        new_row = [name]
                        new_row.extend([
                            f"{formatted_date}",
                            f"{pb['Competition']}",
                            f"{pb['Result'].replace('.', ',')}",
                            f"{', '.join(pb['Records']) if pb['Records'] else '-'}"
                        ])
                        new_rows.append(new_row)
                    else:
                        new_rows.append([name])  # Zachowaj oryginalny wiersz
                else:
                    new_rows.append(row)  # Zachowaj nagłówki
            else:
                new_rows.append(row)  # Zachowaj pozostałe wiersze
        
        # Zapisz do pliku
        with open(original_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(new_rows)
            
        print(f"\n✅ Zaktualizowano plik {original_filename}")
        
    except Exception as e:
        print(f"\n❌ Błąd przy zapisie: {str(e)}")

def print_personal_bests():
    """Główna funkcja przetwarzająca wielu zawodników"""
    # Wybór źródła danych
    print("\nWybierz źródło danych:")
    print("1 - Wprowadź ręcznie (imiona i nazwiska oddzielone przecinkami)")
    print("2 - Wczytaj z pliku (format 9-wierszowy)")
    
    while True:
        choice = input("Twój wybór (1/2): ").strip()
        if choice in ('1', '2'):
            break
        print("Proszę wybrać 1 lub 2")
    
    if choice == '1':
        input_names = input("Podaj imiona i nazwiska zawodników (oddziel przecinkami): ")
        athlete_names = [name.strip() for name in input_names.split(",") if name.strip()]
        output_filename = input("Podaj nazwę pliku do zapisu (domyślnie rekordy.csv): ") or "rekordy.csv"
    else:
        while True:
            original_filename = input("Podaj nazwę pliku z zawodnikami: ").strip()
            if os.path.exists(original_filename):
                break
            print(f"Plik {original_filename} nie istnieje. Spróbuj ponownie.")
        
        # Bierzemy co 9-tą linię zaczynając od pierwszej (indeks 0)
        athlete_names = []
        with open(original_filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i % 9 == 0 and line.strip():
                    name = line.split(',')[0].strip()
                    if name and name != "Data":
                        athlete_names.append(name)
        
        if not athlete_names:
            print("Nie znaleziono zawodników w pliku.")
            return   
        
        print(f"\nZnaleziono {len(athlete_names)} zawodników:")
        print(", ".join(athlete_names[:5]) + ("..." if len(athlete_names) > 5 else ""))
        output_filename = original_filename
    
    if not athlete_names:
        print("Brak zawodników do przetworzenia.")
        return
    
    # Pozostałe parametry
    discipline = input("Podaj dyscyplinę (np. '400mH'): ")
    
    # Przetwarzanie zawodników
    results = []
    for name in athlete_names:
        try:
            print(f"\n• Przetwarzanie: {name}")
            
            athlete_id = find_athlete_id(name)
            if not athlete_id:
                print("❌ Nie znaleziono ID zawodnika")
                continue
                
            pb = get_personal_best(athlete_id, discipline)
            results.append({
                "Name": name,
                "Result": pb["Result"],
                "Date": pb["Date"],
                "Competition": pb["Competition"],
                "Records": pb.get("Records", [])
            })
            print(f"  Znaleziono rekord: {pb['Result']}")
            
        except Exception as e:
            print(f"  ❌ Błąd: {str(e)}")
    
    # Zapis do pliku
    if results:
        if choice == '1':
            save_personal_bests_to_file(results, discipline, output_filename)
        else:
            save_to_same_file(results, output_filename, discipline)
    else:
        print("\n⚠️ Nie znaleziono żadnych wyników do zapisania")

def append_df_to_csv(df, filename, name=None, transpose=False):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', encoding='utf-8-sig', newline='') as f:
        if name:
            if file_exists:
                f.write("\n")  # Dodaj pustą linię przed nowym zawodnikiem jeśli plik istnieje
            f.write(f"{name.title()}\n\n")
        
        # Przygotuj DataFrame do zapisu (transponowany lub nie)
        df_to_save = df.T if transpose else df
        
        # Zapisz dane
        df_to_save.to_csv(f, index=transpose,  # Tylko transponowana tabela ma indeksy
            header=not file_exists if not transpose else True,  # Nagłówki dla nowego pliku lub transponowanej tabeli
            quoting=csv.QUOTE_MINIMAL, escapechar='\\')

def print_results(name, season, file_name, transpose=False):
    athlete_id = find_athlete_id(name)
    print(f"Pobieranie danych dla: {name} (ID: {athlete_id}), sezon: {season}")
    df = get_athlete_results(athlete_id, season)
    append_df_to_csv(df, file_name, name=name, transpose=transpose)
    print(f"✅ Zapisano dane do pliku: {file_name}")

def ask_transpose():
    while True:
        choice = input("Czy transponować dane? (T/N): ").strip().lower()
        if choice in ['t', 'n']:
            return choice == 't'
        print("❌ Nieprawidłowy wybór. Wpisz 'T' lub 'N'.")

def pass_values():
    file_name = input("Podaj nazwę pliku (Enter = domyślnie: wyniki.csv): ").strip() or "wyniki.csv"
    name = input("Podaj imię i nazwisko zawodnika: ")
    season = input("Podaj sezon (np. 2024): ")
    transpose = ask_transpose()
    print_results(name, season, file_name, transpose)

def pass_values_file():
    file_name = input("Podaj nazwę pliku (Enter = domyślnie: wyniki.csv): ").strip() or "wyniki.csv"
    names_input = input("Wklej imiona i nazwiska zawodników oddzielone przecinkami: ")
    season = input("Podaj sezon (np. 2024): ").strip()
    transpose = ask_transpose()

    if not season.isdigit():
        print("❌ Błąd: Sezon musi być liczbą (np. 2024).")
        return

    names = [name.strip() for name in names_input.split(',') if name.strip()]
    if not names:
        print("❌ Błąd: Nie podano żadnych poprawnych imion i nazwisk.")
        return

    for name in names:
        try:
            print_results(name, season, file_name, transpose)
        except ValueError as ve:
            print(f"⚠️ Błąd dla zawodnika '{name}': {ve}")

def pass_values_multiple_seasons():
    file_name = input("Podaj nazwę pliku (Enter = domyślnie: wyniki.csv): ").strip() or "wyniki.csv"
    name = input("Podaj imię i nazwisko zawodnika: ")
    seasons = input("Podaj sezony oddzielone przecinkami (np. 2022,2023,2024): ")
    transpose = ask_transpose()

    for season in seasons.split(','):
        try:
            print_results(name, season.strip(), file_name, transpose)
        except Exception as e:
            print(f"❌ Błąd w sezonie {season.strip()}: {e}")

def pass_multiple_names_and_seasons():
    file_name = input("Podaj nazwę pliku (Enter = domyślnie: wyniki.csv): ").strip() or "wyniki.csv"
    count = int(input("Podaj liczbę zawodników: "))
    transpose = ask_transpose()

    for i in range(count):
        print(f"\nZawodnik {i+1}")
        name = input("Podaj imię i nazwisko zawodnika: ")
        seasons = input("Podaj sezony oddzielone przecinkami (np. 2022,2023): ")
        for season in seasons.split(','):
            try:
                print_results(name, season.strip(), file_name, transpose)
            except Exception as e:
                print(f"❌ Błąd dla {name} w sezonie {season.strip()}: {e}")

def pass_multiple_names_and_multiple_seasons():
    file_name = input("Podaj nazwę pliku (Enter = domyślnie: wyniki.csv): ").strip() or "wyniki.csv"
    transpose = ask_transpose()
    
    # Pobierz liczbę sezonów
    while True:
        num_seasons_input = input("Podaj liczbę sezonów do pobrania: ").strip()
        if num_seasons_input.isdigit() and int(num_seasons_input) > 0:
            num_seasons = int(num_seasons_input)
            break
        print("❌ Błąd: Podaj poprawną liczbę sezonów (większą od 0).")
    
    for i in range(num_seasons):
        print(f"\n=== SEZON {i+1} z {num_seasons} ===")
        names_input = input("Wklej imiona i nazwiska zawodników oddzielone przecinkami: ")
        season = input("Podaj sezon (np. 2024): ").strip()
        
        if not season.isdigit():
            print(f"❌ Błąd: Sezon {season} musi być liczbą. Pomijam ten sezon.")
            continue
        
        names = [name.strip() for name in names_input.split(',') if name.strip()]
        if not names:
            print("❌ Błąd: Nie podano żadnych poprawnych imion i nazwisk. Pomijam ten sezon.")
            continue
        
        for name in names:
            try:
                print_results(name, season, file_name, transpose)
            except ValueError as ve:
                print(f"⚠️ Błąd dla zawodnika '{name}': {ve}")

def is_indoor(event_name):
    """Sprawdza, czy zawody są halowe (np. '(i)', 'indoor', 'hala')"""
    if not isinstance(event_name, str):
        return False
    event_lower = event_name.lower()
    return "(i)" in event_lower or "indoor" in event_lower or "hala" in event_lower

def load_from_csv(filename):
    """Wczytuje dane z CSV, zachowując format nazw zawodów i 64 zawodników"""
    with open(filename, 'r', encoding='utf-8-sig') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    
    athletes = []
    current_athlete = None
    athlete_count = 0
    
    for line in lines:
        # Identyfikacja nowego zawodnika
        if (not line.startswith('Data,') and \
           not line.startswith('Zawody,') and \
           not line.startswith('Konkurencja,') and \
           not line.startswith('Wynik,') and \
           not line.startswith('Punkty,') and \
           not line.startswith(',0,')):
            
            if current_athlete is not None and athlete_count < 64:
                athletes.append(current_athlete)
                athlete_count += 1
            
            current_athlete = {
                'name': line,
                'dates': [],
                'competitions': [],
                'events': [],
                'results': [],
                'points': []
            }
        elif current_athlete is not None:
            # Specjalne przetwarzanie dla zawodów
            if line.startswith('"Zawody,'):
                # Usuwamy początkowe "Zawody, i końcowy cudzysłów
                comp_line = line[len('"Zawody,'):].rstrip('"')
                current_athlete['competitions'] = [comp_line.strip()]
                
            elif line.startswith('Zawody,'):
                # Dla zawodów bez cudzysłowów - standardowe przetwarzanie
                comp_line = line[len('Zawody,'):]
                competitions = []
                current = []
                in_quotes = False
                
                for char in comp_line:
                    if char == '"':
                        in_quotes = not in_quotes
                    elif char == ',' and not in_quotes:
                        competitions.append(''.join(current).strip())
                        current = []
                    else:
                        current.append(char)
                
                if current:
                    competitions.append(''.join(current).strip())
                
                current_athlete['competitions'] = competitions
            
            elif line.startswith('Data,'):
                current_athlete['dates'] = line.split(',')[1:]
            elif line.startswith('Konkurencja,'):
                current_athlete['events'] = line.split(',')[1:]
            elif line.startswith('Wynik,'):
                current_athlete['results'] = line.split(',')[1:]
            elif line.startswith('Punkty,'):
                current_athlete['points'] = line.split(',')[1:]
    
    # Dodaj ostatniego zawodnika jeśli potrzebujemy
    if current_athlete is not None and athlete_count < 64:
        athletes.append(current_athlete)
    
    print(f"Wczytano {len(athletes)} zawodników")
    return athletes

def transform_data(input_data):
    """Poprawiona funkcja transformacji z zachowaniem wszystkich danych"""
    print('\n')
    default_discipline = "400 metres hurdles"
    main_discipline = input(f"Podaj główną dyscyplinę (Enter = {default_discipline}): ").strip() or default_discipline
    output = []
    
    for athlete in input_data:
        # Określamy liczbę kolumn
        num_columns = max(
            len(athlete.get('dates', [])),
            len(athlete.get('competitions', [])),
            len(athlete.get('events', [])),
            len(athlete.get('results', [])),
            len(athlete.get('points', []))
        )
        
        # Inicjalizacja wierszy
        rows = [
            [athlete['name']] + [''] * num_columns,
            ['Data'] + athlete.get('dates', [''] * num_columns),
            ['Starty'] + athlete.get('competitions', [''] * num_columns),
            ['Główny'] + [''] * num_columns,  # Tylko wyniki głównej dyscypliny
            ['Inne'] + [''] * num_columns,    # Tylko nazwy innych dyscyplin
            ['Wyniki Inne'] + [''] * num_columns,  # Wyniki innych dyscyplin
            ['Hala'] + [''] * num_columns,    # Tylko nazwy dyscyplin halowych
            ['Wyniki Hala'] + [''] * num_columns,  # Wyniki dyscyplin halowych
            ['Punkty'] + athlete.get('points', [''] * num_columns)
        ]
        
        # Wypełnianie danych
        for i in range(num_columns):
            event = athlete.get('events', [''] * num_columns)[i] if i < len(athlete.get('events', [])) else ''
            competition = athlete.get('competitions', [''] * num_columns)[i] if i < len(athlete.get('competitions', [])) else ''
            result = athlete.get('results', [''] * num_columns)[i] if i < len(athlete.get('results', [])) else ''
            
            # Zamiana KROPEK na PRZECINKI tylko w wynikach
            if isinstance(result, str):
                result = result.replace('.', ',')

            is_main_discipline = main_discipline.lower() in str(event).lower()
            is_indoor = '(i)' in str(competition).lower() or 'indoor' in str(competition).lower()
            
            if is_main_discipline and not is_indoor:
                rows[3][i+1] = result  # Wynik głównej dyscypliny
            elif is_indoor:
                rows[6][i+1] = event    # Nazwa dyscypliny halowej
                rows[7][i+1] = result   # Wynik dyscypliny halowej
            else:
                if event.strip():  # Jeśli to nie jest pusta dyscyplina
                    rows[4][i+1] = event    # Nazwa innej dyscypliny
                    rows[5][i+1] = result   # Wynik innej dyscypliny
                   
        output.extend(rows)
        #output.append([''] * (num_columns + 1))  # Dodaj pusty wiersz między zawodnikami
    
    return output

def save_to_csv(data, filename):
    """Zapisuje dane dokładnie w formie otrzymanej z transform_data()"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        for row in data:
            # Ręczne formatowanie wiersza
            formatted_row = []
            for item in row:
                if isinstance(item, str):
                    # Zachowujemy oryginalne apostrofy i cudzysłowy
                    formatted_item = item
                    # Dodajemy cudzysłowy tylko jeśli wartość zawiera przecinek
                    if ',' in item and not (item.startswith("'") and item.endswith("'")):
                        formatted_item = f'"{item}"'
                    formatted_row.append(formatted_item)
                else:
                    formatted_row.append(str(item))
            
            # Ręczne łączenie z przecinkami
            f.write(','.join(formatted_row) + '\n')
   
    print(f'Łącznie zapisano {len(data)} wierszy')

def get_output_filename(input_filename):
    """Generuje nazwę pliku wyjściowego na podstawie wejściowego"""
    base, ext = os.path.splitext(input_filename)
    return f"{base}_sformatowane{ext}"

def formatting_data():
    # 1. Pobieranie nazwy pliku od użytkownika
    file_name = input("Podaj nazwę pliku (Enter = domyślnie: wyniki.csv): ").strip() or "wyniki.csv"
    
    # 2. Generowanie nazwy pliku wyjściowego
    output_file = get_output_filename(file_name)
    
    # 3. Wczytanie danych
    print(f"\nPrzetwarzanie pliku: {file_name}")
    data = load_from_csv(file_name)
    
    # 4. Przetworzenie danych
    formatted_data = transform_data(data)
    
    # 5. Zapis wyników
    save_to_csv(formatted_data, output_file)
    print(f"Wyniki zapisano w: {output_file}\n")

def transliterate_to_latin(text):
    """Transliteruje znaki specjalne do podstawowych znaków łacińskich"""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def get_olympic_finalists():
    """Pobiera finalistów z Olympics.com dla wielu lat i zapisuje do pliku"""
    print("\n=== Pobieranie finalistów olimpijskich ===")

    # Pobieranie parametrów
    discipline = input("Podaj dyscyplinę (np. 400MH, 100M, 200M): ").strip().upper()
    if discipline not in DISCIPLINE_MAP:
        print("❌ Nieobsługiwana dyscyplina")
        return

    gender = input("Podaj płeć (men/women): ").strip().lower()
    years_input = input("Podaj lata (oddziel przecinkami, np. 2024, 2021, 2016): ").strip()
    years = [y.strip() for y in years_input.split(',') if y.strip() in OLYMPIC_GAMES]

    if not years:
        print("❌ Brak poprawnych lat do analizy")
        return

    # Pobieranie i przetwarzanie danych
    all_finalists = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    """Buduje URL w zależności od roku igrzysk"""
    base_url = "https://www.olympics.com/en/olympic-games"

    for year in years:
        print(f"\n=== Pobieranie danych dla {year} ===")
        url_part = OLYMPIC_GAMES.get(year)
        discipline_part = DISCIPLINE_MAP.get(discipline)
    
        if not url_part or not discipline_part:
            return None
    
        # Formatowanie dla różnych lat
        if year == "2024":
            url = f"{base_url}/{url_part}/results/athletics/{gender}-{discipline_part}"
        elif year == "2021":
            url = f"{base_url}/{url_part}/results/athletics/{gender}-s-{discipline_part}"
        else:  # Dla lat 2016 i wcześniejszych
            url = f"{base_url}/{url_part}/results/athletics/{discipline_part}-{gender}"
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Bezpośrednie wyszukiwanie displayName w źródle
            html = response.text
            finalists = []
        
            # Wersja 1: Szukamy bezpośrednio w HTML
            display_name_matches = re.findall(r'"displayName":"([^"]+)"', html)
        
            # Wersja 2: Alternatywnie przez BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            script_tags = soup.find_all('script', string=re.compile('displayName'))
        
            for script in script_tags:
                script_matches = re.findall(r'"displayName":"([^"]+)"', script.string)
                finalists.extend(script_matches)
        
            # Filtracja i ograniczenie wyników
            finalists = [name for name in finalists if not any(x in name for x in ['DNS', 'DNF', 'DQ'])]
            finalists = list(dict.fromkeys(finalists))[:8]  # Usuwa duplikaty i ogranicza do 8

            print("\nZnaleziono finalistów:")
            for i, name in enumerate(finalists, 1):
                print(f"{i}. {name}")
                # Dodajemy krotkę (rok, pozycja, nazwisko)
                all_finalists.append((year, i, name))
            else:
                print("❌ Nie znaleziono finalistów")

        except Exception as e:
            print(f"❌ Błąd dla {year}: {str(e)}")

    if not all_finalists:
        print("\n❌ Nie pobrano żadnych danych")
        return

    # Zapis do pliku
    if input("\nCzy zapisać wyniki do pliku? (T/N): ").strip().upper() != 'T':
        return

    filename = input("Podaj nazwę pliku z zawodnikami (domyślnie finaliści.csv): ") or "finaliści.csv"
    format_choice = input("Wybierz format:\n1 - Standardowy (rok,pozycja,zawodnik)\n2 - Specjalny (same nazwiska)\nWybierz (1/2): ").strip()

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if format_choice == '2':
               # Nowy format specjalny - finaliści z każdego roku w osobnej linii
                current_year = None
                for year, _, name in all_finalists:
                    name = transliterate_to_latin(name)
                    if year != current_year:
                        if current_year is not None:
                            f.write('\n')  # Nowa linia dla nowego roku
                        current_year = year
                    else:
                        f.write(', ')
                    f.write(name)
            else:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["Rok", "Pozycja", "Zawodnik"])
                for year, pos, name in all_finalists:
                    name = transliterate_to_latin(name)
                    writer.writerow([year, pos, name])
        
        print(f"\n✅ Wyniki zapisano do: {filename}")

    except Exception as e:
        print(f"\n❌ Błąd zapisu: {str(e)}")

def show_menu():
    print("\n=========== POBIERANIE DANYCH Z WORLD ATHLETICS ===========")
    print("1 - Pobierz dane jednego zawodnika z jednego sezonu")
    print("2 - Pobierz dane wielu zawodników z jednego sezonu")
    print("3 - Pobierz dane jednego zawodnika z wielu sezonów")
    print("4 - Pobierz dane wielu zawodników z wielu sezonów")
    print("5 - Pobierz dane wielu zawodników z wielu sezonów (nowa wersja)")
    print("6 - Formatuj pobrane dane")
    print("7 - Pobierz rekordy życiowe zawodnika")
    print("8 - Pobierz imiona i nazwiska finalistow olimpijskich")
    print("0 - Zakończ program")
    print("===========================================================")
    print('\n')

def main():
    while True:
        show_menu()
        select = input("Wybierz opcję: ").strip()
        if select == "1":
            pass_values()
        elif select == "2":
            pass_values_file()
        elif select == "3":
            pass_values_multiple_seasons()
        elif select == "4":
            pass_multiple_names_and_seasons()
        elif select == "5":
            pass_multiple_names_and_multiple_seasons()
        elif select == "6":
            formatting_data()
        elif select == "7":
            print_personal_bests()
        elif select == "8":
            get_olympic_finalists()
        elif select == "0":
            print("Zakończono program.")
            break
        else:
            print("❌ Nieprawidłowy wybór. Spróbuj ponownie.")

if __name__ == "__main__":
    main()
