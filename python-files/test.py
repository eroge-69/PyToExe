import serial
import sys

def apri_seriale():
    while True:
        porta = input("Inserisci porta COM (es. COM9): ").strip().upper()
        try:
            s = serial.Serial(porta, 9600, timeout=1)
            print(f"✅ Connesso a {porta}\n")
            return s
        except:
            print(f"❌ Porta {porta} non valida. Riprova.")

ser = apri_seriale()

print("🟢 Inserisci il dato da scrivere (max 15 caratteri). Digita 'exit' per uscire.")

while True:
    try:
        stringa = input(">> ").strip()
        if stringa.lower() == "exit":
            break
        if len(stringa) == 0:
            continue
        if len(stringa) > 15:
            print("❌ Troppo lungo. Max 15 caratteri.")
            continue
        padded = stringa.rjust(15, '0')
        ser.write((padded + "\r").encode('utf-8'))
        print("✅ Inviato:", padded)
    except Exception as e:
        print("Errore:", e)
