import os
import json
import argparse
import time

# --- POMOCNICZE FUNKCJE ---

def seconds_to_srt_time(seconds):
    try:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
    except (TypeError, ValueError):
        return "00:00:00,000"

# --- GŁÓWNE FUNKCJE PRZETWARZANIA ---

def json_to_srt(json_path, target_lang, source_lang):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Błąd wczytywania pliku JSON '{json_path}': {e}")
        return

    segments = []
    possible_locations = ['segments', 'transcribe', 'text_segments', 'data']
    for loc in possible_locations:
        if loc in data and isinstance(data[loc], list):
            segments = data[loc]
            break

    if not segments:
        return

    base_name = os.path.splitext(json_path)[0]
    srt_path = f"{base_name}-eng.srt"

    print(f"\nPrzetwarzanie pliku: {os.path.basename(json_path)}")
    print(f"Znaleziono segmentów: {len(segments)}")
    print(f"Tłumaczenie pominięte – zachowuję oryginalny tekst.")

    with open(srt_path, 'w', encoding='utf-8') as srt_file:
        for i, segment in enumerate(segments, 1):
            try:
                if isinstance(segment, dict):
                    start = segment.get('start', segment.get('start_time', 0))
                    end = segment.get('end', segment.get('end_time', 0))
                    text = segment.get('text', '').strip()
                elif isinstance(segment, str):
                    start = i - 1
                    end = i
                    text = segment.strip()
                else:
                    print(f"Ostrzeżenie: Nieoczekiwany format segmentu {i}. Pomijam.")
                    continue

                if not text:
                    continue

                translated_text = text  # Pomijamy tłumaczenie
                print(f"\rPrzetworzono segment {i}/{len(segments)} (bez tłumaczenia)", end='', flush=True)

                srt_file.write(f"{i}\n{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n{translated_text}\n\n")

            except Exception as e:
                print(f"\nBłąd segmentu {i} w pliku '{json_path}': {e}")
                continue

    print(f"\nPlik SRT zapisano jako: {srt_path}")

def process_directory(directory, source_lang, target_lang):
    if not os.path.exists(directory):
        print(f"Błąd: Katalog nie istnieje: {directory}")
        return

    print(f"\nPrzeszukiwanie katalogu: {directory}")
    files_processed = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.json') and 'metadata' not in file.lower() and 'stats' not in file.lower():
                full_path = os.path.join(root, file)
                json_to_srt(full_path, target_lang, source_lang)
                files_processed += 1

    if files_processed == 0:
        print("Nie znaleziono odpowiednich plików JSON w katalogu.")

# --- GŁÓWNA FUNKCJA PROGRAMU ---

def main():
    parser = argparse.ArgumentParser(
        description="Konwertuj JSON z napisami na SRT bez tłumaczenia.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_path",
        help="Ścieżka do pliku JSON lub katalogu z plikami JSON do przetworzenia."
    )
    parser.add_argument(
        "-t", "--target",
        default="pl",
        help="Język docelowy (nazwa pliku SRT zostanie do niego dopasowana). Domyślnie: 'pl'."
    )
    parser.add_argument(
        "-s", "--source",
        default="en",
        help="Język źródłowy. Domyślnie: 'en'."
    )

    args = parser.parse_args()
    input_path = args.input_path.strip('"\'')
    
    print("\n--- Start ---")
    print(f"Źródło: {args.source} | Docelowy język nazw pliku: {args.target}")
    print("Tłumaczenie wyłączone – oryginalny tekst zostaje zachowany.")
    print("--------------------------------------")

    if os.path.isfile(input_path):
        json_to_srt(input_path, args.target, args.source)
    elif os.path.isdir(input_path):
        process_directory(input_path, args.source, args.target)
    else:
        print(f"Błąd: Ścieżka '{input_path}' nie jest ani plikiem, ani katalogiem.")

    print("\n--- Zakończono ---")

if __name__ == "__main__":
    main()