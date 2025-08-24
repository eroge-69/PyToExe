import pyautogui
import pytesseract
from PIL import Image
import time
import threading
import tkinter as tk
from tkinter import messagebox

# Imposta percorso Tesseract (modifica se installato in un'altra cartella)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

running = False  # variabile globale per avvio/stop

def find_and_click(text_to_find):
    screenshot = pyautogui.screenshot()
    data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

    for i, word in enumerate(data["text"]):
        if text_to_find.lower() in word.lower():
            x = data["left"][i] + data["width"][i] // 2
            y = data["top"][i] + data["height"][i] // 2
            pyautogui.click(x, y)
            print(f"[OK] Cliccato su: {word} ({x},{y})")
            return True
    print("[X] Testo non trovato in questo ciclo.")
    return False

def worker(text, interval):
    global running
    while running:
        find_and_click(text)
        time.sleep(interval)

def start_search():
    global running
    if running:
        return
    text = entry_text.get().strip()
    try:
        interval = float(entry_interval.get())
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un numero valido per l'intervallo")
        return
    if not text:
        messagebox.showerror("Errore", "Inserisci una parola da cercare")
        return
    
    running = True
    threading.Thread(target=worker, args=(text, interval), daemon=True).start()
    messagebox.showinfo("Avvio", f"Ricerca di '{text}' ogni {interval} secondi avviata!")

def stop_search():
    global running
    running = False
    messagebox.showinfo("Stop", "Ricerca interrotta.")

# GUI Tkinter
root = tk.Tk()
root.title("Salta Video")   # titolo finestra

tk.Label(root, text="Parola da cercare:").pack(pady=5)
entry_text = tk.Entry(root, width=30)
entry_text.pack(pady=5)

tk.Label(root, text="Intervallo (secondi):").pack(pady=5)
entry_interval = tk.Entry(root, width=10)
entry_interval.pack(pady=5)

tk.Button(root, text="Avvia ricerca", command=start_search, bg="green", fg="white").pack(pady=10)
tk.Button(root, text="Stop", command=stop_search, bg="red", fg="white").pack(pady=5)

root.mainloop()
