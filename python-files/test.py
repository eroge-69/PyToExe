import serial
import sys

def apri_seriale():
    """Chiede all'utente di inserire una porta COM e la apre."""
    while True:
        porta = input("Inserisci porta COM (es. COM9): ").strip().upper()
        try:
            # Tenta di aprire la porta con un timeout di 1 secondo
            s = serial.Serial(porta, 9600, timeout=1)
            print(f"Connesso a {porta}\n")
            return s
        except serial.SerialException: # Cattura l'eccezione specifica
            print(f"Porta {porta} non valida o non accessibile. Riprova.")

# --- Inizio del programma principale ---

ser = apri_seriale()

print("🟢 Inserisci il dato da scrivere (max 15 caratteri). Digita 'exit' per uscire.")

try:
    while True:
        stringa = input(">> ").strip()

        if stringa.lower() == "exit":
            print("Chiusura programma.")
            break # Esce dal loop

        if not stringa: # Un modo più "pythonico" per controllare se la stringa è vuota
            continue

        if len(stringa) > 15:
            print("Troppo lungo. Max 15 caratteri.")
            continue

        # Aggiunge '0' a sinistra fino a raggiungere 15 caratteri
        padded = stringa.rjust(15, '0')

        # Invia i dati sulla seriale, codificati in UTF-8
        ser.write((padded + "\r").encode('utf-8'))
        print("Inviato:", padded)

except (KeyboardInterrupt, Exception) as e:
    # Cattura l'interruzione da tastiera (CTRL+C) o altri errori
    print(f"\nErrore: {e}")

finally:
    # Questo blocco viene eseguito SEMPRE, sia in caso di uscita normale che di errore
    if ser and ser.is_open:
        ser.close()
        print("Porta seriale chiusa.")