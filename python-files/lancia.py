import tkinter as tk
import subprocess
import sys

def open_chrome():
    """Lancia Google Chrome."""
    try:
        subprocess.Popen(['start', 'chrome'], shell=True)
    except FileNotFoundError:
        print("Google Chrome non trovato. Assicurati che sia installato e nel tuo PATH.")

def open_firefox():
    """Lancia Mozilla Firefox."""
    try:
        subprocess.Popen(['start', 'firefox'], shell=True)
    except FileNotFoundError:
        print("Mozilla Firefox non trovato. Assicurati che sia installato e nel tuo PATH.")

def close_program():
    """Chiude il programma."""
    sys.exit()

# Crea la finestra principale
root = tk.Tk()
root.title("Lancia Browser")
root.geometry("300x200") # Imposta le dimensioni della finestra

# Crea il bottone per Chrome
button_chrome = tk.Button(root, text="Chrome", command=open_chrome, width=20, height=2)
button_chrome.pack(pady=10) # Aggiunge spazio verticale

# Crea il bottone per Firefox
button_firefox = tk.Button(root, text="Firefox", command=open_firefox, width=20, height=2)
button_firefox.pack(pady=10)

# Crea il bottone per chiudere il programma
button_close = tk.Button(root, text="Chiudi Programma", command=close_program, width=20, height=2)
button_close.pack(pady=10)

# Avvia il loop principale della finestra
root.mainloop()