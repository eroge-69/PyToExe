import os
import sys
import webbrowser
import urllib.parse
import subprocess
import tkinter as tk
from tkinter import messagebox

APP_NAME = "documentazione"
RECIPIENT = "g.fiorente@confarmstudio.it"
SUBJECT = "Documentazione – Dati anagrafici"

def open_default_mail(nome: str, cognome: str, cambiamenti: str) -> None:
    body_lines = [
        "Dati anagrafici raccolti dall'app 'documentazione':",
        "",
        f"Nome: {nome}",
        f"Cognome: {cognome}",
        "",
        "Cambiamenti immobili:",
        (cambiamenti.strip() or "(non specificato)")
    ]
    body = "\n".join(body_lines)

    params = {"subject": SUBJECT, "body": body}
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    mailto_url = f"mailto:{RECIPIENT}?{query}"

    if sys.platform.startswith("win") and hasattr(os, "startfile"):
        os.startfile(mailto_url)
    elif sys.platform == "darwin":
        subprocess.run(["open", mailto_url], check=False)
    elif sys.platform.startswith("linux"):
        try:
            subprocess.run(["xdg-email", "--subject", SUBJECT, "--body", body, RECIPIENT], check=False)
        except Exception:
            webbrowser.open(mailto_url)
    else:
        webbrowser.open(mailto_url)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.configure(bg="#f0f7ff")
        self.resizable(False, False)

        title = tk.Label(self, text="Raccolta dati anagrafici", font=("Segoe UI", 16, "bold"), bg="#2563eb", fg="white", padx=16, pady=10)
        title.grid(row=0, column=0, sticky="ew")

        container = tk.Frame(self, bg="#f0f7ff", padx=16, pady=16)
        container.grid(row=1, column=0)

        card = tk.Frame(container, bg="white")
        card.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
        card.grid_columnconfigure(1, weight=1)

        tk.Label(card, text="Nome", bg="white").grid(row=0, column=0, sticky="w")
        self.nome_var = tk.StringVar()
        tk.Entry(card, textvariable=self.nome_var).grid(row=0, column=1, sticky="ew")

        tk.Label(card, text="Cognome", bg="white").grid(row=1, column=0, sticky="w")
        self.cognome_var = tk.StringVar()
        tk.Entry(card, textvariable=self.cognome_var).grid(row=1, column=1, sticky="ew")

        tk.Label(card, text="Cambiamenti immobili", bg="white").grid(row=2, column=0, sticky="nw")
        self.cambiamenti_text = tk.Text(card, height=6, width=40)
        self.cambiamenti_text.grid(row=2, column=1, sticky="ew")

        buttons = tk.Frame(container, bg="#f0f7ff")
        buttons.grid(row=1, column=0, pady=10)
        tk.Button(buttons, text="Apri email", command=self.on_invia, bg="#10b981", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(buttons, text="Reset", command=self.on_reset).pack(side=tk.LEFT, padx=5)

    def on_reset(self):
        self.nome_var.set("")
        self.cognome_var.set("")
        self.cambiamenti_text.delete("1.0", tk.END)

    def on_invia(self):
        nome = self.nome_var.get().strip()
        cognome = self.cognome_var.get().strip()
        cambiamenti = self.cambiamenti_text.get("1.0", tk.END)
        if not nome or not cognome:
            messagebox.showwarning("Campi obbligatori", "Inserisci Nome e Cognome")
            return
        open_default_mail(nome, cognome, cambiamenti)
        messagebox.showinfo("Bozza creata", "Controlla e invia dal tuo client di posta.")

def main():
    app = App()
    w, h = 520, 480
    x = (app.winfo_screenwidth() // 2) - (w // 2)
    y = (app.winfo_screenheight() // 2) - (h // 2)
    app.geometry(f"{w}x{h}+{x}+{y}")
    app.mainloop()

if __name__ == "__main__":
    main()

"""
COMANDO PRONTO PER CREARE documentazione.exe SUL DESKTOP (Windows):

pip install pyinstaller && pyinstaller --onefile --noconsole --distpath "%USERPROFILE%\\Desktop" documentazione.py

Questo comando installerà PyInstaller (se non presente), compilerà il file e metterà l'eseguibile direttamente sul Desktop.
"""
