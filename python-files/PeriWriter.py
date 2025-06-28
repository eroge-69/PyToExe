import tkinter as tk
import socket
import os
from datetime import datetime

# ⚙️ Konfiguracja
PRINTER_MAC = '00:11:22:33:44:55'  # ← Zamień na adres MAC swojej drukarki PeriPage
PORT = 1
LOGO_PATH = 'logo.bmp'
HISTORIA_FOLDER = 'wydruki'

# 🖨️ Połączenie Bluetooth
def polacz():
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((PRINTER_MAC, PORT))
    return s

# 🖨️ Wysyłanie tekstu
def drukuj_tekst():
    tekst = pole.get("1.0", tk.END).strip()
    if not tekst:
        status.set("⚠️ Brak tekstu do wydruku.")
        return
    try:
        s = polacz()
        s.send(bytes(tekst + '\n\n', 'utf-8'))
        s.close()
        zapisz_historie(tekst)
        status.set("✅ Tekst wydrukowany.")
    except Exception as e:
        status.set(f"Błąd: {e}")

# 🖼️ Wysyłanie pliku logo.bmp
def drukuj_logo():
    if not os.path.exists(LOGO_PATH):
        status.set("⚠️ Plik logo.bmp nie znaleziony.")
        return
    try:
        with open(LOGO_PATH, 'rb') as f:
            dane = f.read()
        s = polacz()
        s.send(b'\x1B\x40')  # ESC @ - reset
        s.send(dane)
        s.close()
        status.set("🖼️ Logo wydrukowane.")
    except Exception as e:
        status.set(f"Błąd: {e}")

# 💾 Zapis historii
def zapisz_historie(tresc):
    if not os.path.exists(HISTORIA_FOLDER):
        os.makedirs(HISTORIA_FOLDER)
    plik = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.txt")
    sciezka = os.path.join(HISTORIA_FOLDER, plik)
    with open(sciezka, 'w', encoding='utf-8') as f:
        f.write(tresc)

# 🪟 Interfejs tkinter
okno = tk.Tk()
okno.title("PeriWriter GUI")

pole = tk.Text(okno, height=10, width=50, font=("Segoe UI", 12))
pole.pack(padx=10, pady=10)

bt_drukuj = tk.Button(okno, text="🖨️ Drukuj tekst", command=drukuj_tekst)
bt_drukuj.pack(fill='x', padx=20, pady=5)

bt_logo = tk.Button(okno, text="🖼️ Drukuj logo", command=drukuj_logo)
bt_logo.pack(fill='x', padx=20, pady=5)

status = tk.StringVar()
status_label = tk.Label(okno, textvariable=status, fg="green")
status_label.pack(pady=10)

okno.mainloop()
