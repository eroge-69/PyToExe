
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

DATA_FILE = "patients_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class MedicalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestione Studio Medico")
        self.data = load_data()

        self.main_menu()

    def main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Studio Medico - Menu Principale", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="Inserisci Paziente", width=30, command=self.insert_patient).pack(pady=5)
        tk.Button(self.root, text="Ricerca Paziente", width=30, command=self.search_patient).pack(pady=5)
        tk.Button(self.root, text="Cartella Clinica", width=30, command=self.edit_clinical_record).pack(pady=5)
        tk.Button(self.root, text="Fatturazione", width=30, command=self.billing).pack(pady=5)
        tk.Button(self.root, text="Stampa Riepilogo", width=30, command=self.print_summary).pack(pady=5)

    def insert_patient(self):
        name = simpledialog.askstring("Inserisci Paziente", "Nome e Cognome:")
        if name:
            if name in self.data:
                messagebox.showinfo("Info", "Paziente già esistente.")
            else:
                self.data[name] = {"cartella": "", "fatture": []}
                save_data(self.data)
                messagebox.showinfo("Successo", "Paziente inserito.")

    def search_patient(self):
        name = simpledialog.askstring("Ricerca Paziente", "Nome e Cognome:")
        if name in self.data:
            messagebox.showinfo("Trovato", f"Paziente: {name}")
        else:
            messagebox.showerror("Errore", "Paziente non trovato.")

    def edit_clinical_record(self):
        name = simpledialog.askstring("Cartella Clinica", "Nome e Cognome:")
        if name in self.data:
            record = simpledialog.askstring("Cartella Clinica", "Inserisci/Modifica cartella clinica:", initialvalue=self.data[name]["cartella"])
            if record is not None:
                self.data[name]["cartella"] = record
                save_data(self.data)
                messagebox.showinfo("Successo", "Cartella aggiornata.")
        else:
            messagebox.showerror("Errore", "Paziente non trovato.")

    def billing(self):
        name = simpledialog.askstring("Fatturazione", "Nome e Cognome:")
        if name in self.data:
            amount = simpledialog.askfloat("Fatturazione", "Importo fattura:")
            if amount is not None:
                self.data[name]["fatture"].append(amount)
                save_data(self.data)
                messagebox.showinfo("Successo", "Fattura registrata.")
        else:
            messagebox.showerror("Errore", "Paziente non trovato.")

    def print_summary(self):
        summary = ""
        for name, info in self.data.items():
            summary += f"Paziente: {name}\nCartella: {info['cartella']}\nFatture: {info['fatture']}\n\n"
        if summary:
            summary_window = tk.Toplevel(self.root)
            summary_window.title("Riepilogo Pazienti")
            text = tk.Text(summary_window, wrap=tk.WORD)
            text.insert(tk.END, summary)
            text.pack(expand=True, fill=tk.BOTH)
        else:
            messagebox.showinfo("Info", "Nessun dato disponibile.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalApp(root)
    root.mainloop()
