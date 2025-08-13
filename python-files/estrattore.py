import tkinter as tk
from tkinter import messagebox
import random
import os
import sys

def nascondi_console():
    """
    Nasconde la console su Windows (quando eseguito con python.exe).
    Ignorato se già avviato con pythonw.exe o su altri OS.
    """
    if os.name == "nt":
        try:
            import ctypes
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
        except Exception:
            pass

class EstrazioneApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="black")
        self.root.title("🎲 Estrazione Casuale by Bad89")
        self.root.geometry("1000x650")
        self.root.resizable(False, False)

        # Titolo
        tk.Label(root, text="INSERISCI I NOMI (UNO PER RIGA)", font=("Papyrus", 12), fg="red").pack(pady=10)

        # Textbox per i nomi
        self.text_nomi = tk.Text(root, height=30, width=80)
        self.text_nomi.pack()

        # Bottone di estrazione
        tk.Button(root, text="ESTRAI NOME", font=("Arial Black", 14, "bold"),
                  bg="#FF0000", fg="white", command=self.estrai_nome).pack(pady=15)

        # Etichetta risultato
        self.risultato_label = tk.Label(root, text="", font=("Arial", 16, "bold"), bg="black", fg="white")
        self.risultato_label.pack(pady=10)

    def estrai_nome(self):
        nomi = self.text_nomi.get("1.0", tk.END).strip().split("\n")
        nomi = [n.strip() for n in nomi if n.strip() != ""]

        if not nomi:
            messagebox.showwarning("Attenzione", "Inserisci almeno un nome.")
            return

        estratto = random.choice(nomi)
        self.risultato_label.config(text=f"🎉 Estratto: {estratto}")

def main():
    nascondi_console()
    root = tk.Tk()
    app = EstrazioneApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
