import tkinter as tk
from tkinter import ttk
import csv
import os
from datetime import datetime

FILE_ORDINI = "ordini.csv"

# Carica dati esistenti
def carica_ordini():
    if not os.path.exists(FILE_ORDINI):
        return []
    with open(FILE_ORDINI, newline='', encoding='utf-8') as csvfile:
        return list(csv.DictReader(csvfile))

# Salva i dati
def salva_ordini():
    with open(FILE_ORDINI, "w", newline='', encoding='utf-8') as csvfile:
        campi = ["data", "cantiere", "litri", "capo_cantiere", "completato"]
        writer = csv.DictWriter(csvfile, fieldnames=campi)
        writer.writeheader()
        for ordine in ordini:
            writer.writerow(ordine)

# Aggiunge un nuovo ordine
def aggiungi_ordine():
    ordine = {
        "data": entry_data.get(),
        "cantiere": entry_cantiere.get(),
        "litri": entry_litri.get(),
        "capo_cantiere": entry_capo.get(),
        "completato": "NO"
    }
    ordini.append(ordine)
    salva_ordini()
    aggiorna_lista()
    entry_data.delete(0, tk.END)
    entry_cantiere.delete(0, tk.END)
    entry_litri.delete(0, tk.END)
    entry_capo.delete(0, tk.END)

# Cambia lo stato del completamento
def toggle_completato(index):
    ordine = ordini[index]
    ordine["completato"] = "SI" if ordine["completato"] == "NO" else "NO"
    salva_ordini()
    aggiorna_lista()

# Aggiorna la visualizzazione
def aggiorna_lista():
    for widget in frame_lista.winfo_children():
        widget.destroy()

    ordini_ordinati = sorted(ordini, key=lambda x: datetime.strptime(x["data"], "%Y-%m-%d"))

    for i, ordine in enumerate(ordini_ordinati):
        testo = f"{ordine['data']} - {ordine['cantiere']} - {ordine['litri']} L - {ordine['capo_cantiere']}"
        stato = ordine["completato"]
        colore = "green" if stato == "SI" else "red"
        chk = tk.Checkbutton(frame_lista, text=teso, fg=colore, anchor="w",
                             command=lambda i=i: toggle_completato(ordini.index(ordini_ordinati[i])))
        chk.pack(fill='x', padx=5, pady=2)
        if stato == "SI":
            chk.select()

# GUI
root = tk.Tk()
root.title("Ordini Gasolio - Cantieri")
root.geometry("500x600")

frame_input = tk.Frame(root)
frame_input.pack(pady=10)

tk.Label(frame_input, text="Data (YYYY-MM-DD):").grid(row=0, column=0, sticky="e")
entry_data = tk.Entry(frame_input)
entry_data.grid(row=0, column=1)

tk.Label(frame_input, text="Cantiere:").grid(row=1, column=0, sticky="e")
entry_cantiere = tk.Entry(frame_input)
entry_cantiere.grid(row=1, column=1)

tk.Label(frame_input, text="Litri:").grid(row=2, column=0, sticky="e")
entry_litri = tk.Entry(frame_input)
entry_litri.grid(row=2, column=1)

tk.Label(frame_input, text="Capo Cantiere:").grid(row=3, column=0, sticky="e")
entry_capo = tk.Entry(frame_input)
entry_capo.grid(row=3, column=1)

btn_aggiungi = tk.Button(root, text="Aggiungi Ordine", command=aggiungi_ordine)
btn_aggiungi.pack(pady=5)

frame_lista = tk.Frame(root)
frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

# Dati iniziali
ordini = carica_ordini()
aggiorna_lista()

root.mainloop()
