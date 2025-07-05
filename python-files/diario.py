import csv
from datetime import datetime

FILENAME = "diario_pressorio.csv"

def inizializza_file():
    try:
        with open(FILENAME, mode='x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Data", "Ora", "Sistolica", "Diastolica", "Frequenza", "Posizione", "Note"])
    except FileExistsError:
        pass  # Il file esiste già

def registra_misurazione():
    data = datetime.now().strftime("%Y-%m-%d")
    ora = datetime.now().strftime("%H:%M")
    sistolica = input("Inserisci la pressione sistolica (mmHg): ")
    diastolica = input("Inserisci la pressione diastolica (mmHg): ")
    frequenza = input("Inserisci la frequenza cardiaca (bpm): ")
    posizione = input("Posizione (seduto/in piedi): ")
    note = input("Note (sintomi, farmaci, ecc.): ")

    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([data, ora, sistolica, diastolica, frequenza, posizione, note])
    print("✅ Misurazione registrata con successo!")

def mostra_riepilogo():
    try:
        with open(FILENAME, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Salta l'intestazione
            print("\n📊 Riepilogo Misurazioni:")
            for row in reader:
                print(" | ".join(row))
    except FileNotFoundError:
        print("⚠️ Nessun dato trovato. Registra prima una misurazione.")

def menu():
    inizializza_file()
    while True:
        print("\n--- Diario Pressorio ---")
        print("1. Registra nuova misurazione")
        print("2. Mostra riepilogo")
        print("3. Esci")
        scelta = input("Scegli un'opzione: ")

        if scelta == "1":
            registra_misurazione()
        elif scelta == "2":
            mostra_riepilogo()
        elif scelta == "3":
            print("👋 Uscita dal programma.")
            break
        else:
            print("❌ Scelta non valida. Riprova.")

if __name__ == "__main__":
    menu()

