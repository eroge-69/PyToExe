#!/usr/bin/env python3
# qr_generator.py

import sys
import io
import requests
import pandas as pd
import qrcode
from tkinter import Tk, Label, Button, Entry, StringVar, ttk, messagebox
from PIL import Image, ImageTk

# URL des Markdown-ValueSets (liefert HTML-Render)
URL = "https://simplifier.net/guide/KDL/Hauptseite/ValueSet-duplicate-2.guide.md?version=current"

class QRApp:
    def __init__(self, master):
        self.master = master
        master.title("QR‑Code Generator für KDL")

        # Variablen
        self.display_var = StringVar(master)
        self.free_var    = StringVar(master)
        self.value_map   = {}  # Display -> Code

        # UI‑Elemente
        Label(master, text="Eintrag wählen (Display):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo = ttk.Combobox(master, textvariable=self.display_var, state="readonly", width=40)
        self.combo.grid(row=0, column=1, padx=5, pady=5)

        Label(master, text="Freier Wert:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        Entry(master, textvariable=self.free_var, width=43).grid(row=1, column=1, padx=5, pady=5)

        Button(master, text="QR‑Code erzeugen", command=self.generate_qr).grid(row=2, column=0, columnspan=2, pady=10)

        self.img_label = Label(master)
        self.img_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Lade die Werte beim Start
        self.fetch_values()

    def fetch_values(self):
        try:
            resp = requests.get(URL, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            messagebox.showerror("Fehler", f"Kann ValueSet nicht laden:\n{e}")
            sys.exit(1)

        # pandas.read_html kann aus dem HTML die Markdown‑Tabelle extrahieren
        tables = pd.read_html(resp.text)
        if not tables:
            messagebox.showerror("Fehler", "Keine Tabellen gefunden in der Antwort.")
            sys.exit(1)

        # erste Tabelle auswählen, Spalten prüfen
        df = tables[0]
        if not {"Code", "Display"}.issubset(df.columns):
            messagebox.showerror("Fehler", "Erwartete Spalten 'Code' und 'Display' nicht gefunden.")
            sys.exit(1)

        # Map und Combobox füllen
        self.value_map = dict(zip(df["Display"], df["Code"]))
        self.combo["values"] = list(self.value_map.keys())
        if self.value_map:
            self.combo.current(0)

    def generate_qr(self):
        disp = self.display_var.get()
        free = self.free_var.get().strip()
        if not disp:
            messagebox.showwarning("Hinweis", "Bitte erst einen Eintrag auswählen.")
            return
        code = self.value_map.get(disp, "")
        # QR‑Code-Text zusammenbauen
        qr_text = f"GUN&{code}&{free}"
        # QR‑Code generieren
        img = qrcode.make(qr_text)
        # PIL → Tkinter
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        bio.seek(0)
        tk_img = ImageTk.PhotoImage(Image.open(bio))
        self.img_label.configure(image=tk_img)
        self.img_label.image = tk_img  # Referenz halten
        # Optional: Bild speichern
        try:
            img.save("last_qr.png")
        except:
            pass

if __name__ == "__main__":
    root = Tk()
    app = QRApp(root)
    root.mainloop()
