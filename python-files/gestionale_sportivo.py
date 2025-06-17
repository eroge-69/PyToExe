import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import credit_card
from reportlab.pdfgen import canvas

# Percorso base salvataggio
BASE_DIR = r"C:\ArchivioSportivo"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionale Sportivo")
        self.root.geometry("400x400")

        # Variabili
        self.data = {}

        # Interfaccia
        self.create_form()

    def create_form(self):
        labels = ["Nome", "Cognome", "Data di nascita (GG/MM/AAAA)", "Telefono", "Email"]
        self.entries = {}

        for idx, label in enumerate(labels):
            tk.Label(self.root, text=label).pack()
            entry = tk.Entry(self.root)
            entry.pack()
            self.entries[label] = entry

        # Pulsanti documenti
        tk.Button(self.root, text="Carica Certificato Medico", command=lambda: self.carica_file("certificato_medico")).pack(pady=5)
        tk.Button(self.root, text="Carica Documento Identità", command=lambda: self.carica_file("documento_identita")).pack(pady=5)

        # Salva
        tk.Button(self.root, text="Salva e Genera Tessera", command=self.salva_dati).pack(pady=20)

    def carica_file(self, tipo):
        file_path = filedialog.askopenfilename(title=f"Seleziona {tipo}")
        if file_path:
            self.data[tipo] = file_path
            messagebox.showinfo("OK", f"{tipo} caricato.")

    def salva_dati(self):
        nome = self.entries["Nome"].get().strip()
        cognome = self.entries["Cognome"].get().strip()
        data_nascita = self.entries["Data di nascita (GG/MM/AAAA)"].get().strip()

        if not nome or not cognome or not data_nascita:
            messagebox.showerror("Errore", "Inserire almeno nome, cognome e data di nascita.")
            return

        cartella_utente = os.path.join(BASE_DIR, f"{nome}_{cognome}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(cartella_utente, exist_ok=True)

        # Salva JSON con i dati
        self.data.update({
            "nome": nome,
            "cognome": cognome,
            "data_nascita": data_nascita,
            "telefono": self.entries["Telefono"].get().strip(),
            "email": self.entries["Email"].get().strip()
        })

        with open(os.path.join(cartella_utente, "dati.json"), "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

        # Copia documenti
        for tipo in ["certificato_medico", "documento_identita"]:
            if tipo in self.data:
                file_name = os.path.basename(self.data[tipo])
                os.system(f'copy "{self.data[tipo]}" "{os.path.join(cartella_utente, file_name)}"')

        # Genera tessera PDF
        self.genera_tessera(self.data, cartella_utente)

        messagebox.showinfo("Fatto", "Dati salvati e tessera generata.")
        self.root.quit()

    def genera_tessera(self, dati, path):
        tessera_path = os.path.join(path, "tessera_abbonamento.pdf")
        c = canvas.Canvas(tessera_path, pagesize=credit_card)
        c.setFont("Helvetica-Bold", 10)

        c.drawString(30, 50, f"Nome: {dati['nome']} {dati['cognome']}")
        c.drawString(30, 40, f"Nascita: {dati['data_nascita']}")
        rilascio = datetime.today().strftime("%d/%m/%Y")
        scadenza = (datetime.today() + timedelta(days=365)).strftime("%d/%m/%Y")
        c.drawString(30, 30, f"Rilasciata il: {rilascio}")
        c.drawString(30, 20, f"Valida fino al: {scadenza}")

        c.showPage()
        c.save()
