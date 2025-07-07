import csv
from datetime import datetime

# Nome del file CSV
CSV_FILE = "monitoraggio_pressione.csv"

# Intestazioni del file CSV
HEADER = ["Data", "Ora", "Pressione Massima", "Pressione Minima", "Frequenza Cardiaca", "Note"]

# Funzione per inizializzare il file CSV se non esiste
def inizializza_csv():
    try:
        with open(CSV_FILE, mode='x', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(HEADER)
            print(f"✅ File '{CSV_FILE}' creato con intestazioni.")
    except FileExistsError:
        pass  # Il file esiste già

# Funzione per aggiungere una nuova misurazione
def aggiungi_misurazione():
    data = input("📅 Inserisci la data (YYYY-MM-DD) [lascia vuoto per oggi]: ")
    ora = input("⏰ Inserisci l'ora (HH:MM) [lascia vuoto per ora attuale]: ")

    if not data:
        data = datetime.now().strftime("%Y-%m-%d")
    if not ora:
        ora = datetime.now().strftime("%H:%M")

    try:
        sistolica = int(input("🔴 Pressione massima (sistolica): "))
        diastolica = int(input("🔵 Pressione minima (diastolica): "))
        frequenza = int(input("❤️ Frequenza cardiaca (bpm): "))
    except ValueError:
        print("⚠️ Inserisci solo numeri interi per pressione e frequenza.")
        return

    note = input("📝 Note (facoltative): ")

    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([data, ora, sistolica, diastolica, frequenza, note])
        print("✅ Misurazione salvata con successo.")

# Funzione principale
def main():
    inizializza_csv()
    while True:
        aggiungi_misurazione()
        continua = input("➕ Vuoi inserire un'altra misurazione? (s/n): ").lower()
        if continua != 's':
            print("👋 Uscita dal programma.")
            break

if __name__ == "__main__":
    main()
