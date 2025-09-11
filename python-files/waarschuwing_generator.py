import tkinter as tk
from tkinter import ttk, messagebox
from docx import Document
from datetime import datetime
import os

def generate_brief():
    naam = entry_naam.get()
    kamer = entry_kamer.get()
    datum = entry_datum.get()
    waarschuwing = combo_waarschuwing.get()

    if not naam or not kamer or not datum or not waarschuwing:
        messagebox.showerror("Fout", "Vul alle velden in!")
        return

    try:
        # Sjabloon openen
        doc = Document("Huisstijl_NKZ_template.docx")

        # Placeholders vervangen
        for p in doc.paragraphs:
            if "{{naam}}" in p.text:
                p.text = p.text.replace("{{naam}}", naam)
            if "{{kamer}}" in p.text:
                p.text = p.text.replace("{{kamer}}", kamer)
            if "{{datum}}" in p.text:
                p.text = p.text.replace("{{datum}}", datum)
            if "{{waarschuwing}}" in p.text:
                p.text = p.text.replace("{{waarschuwing}}", waarschuwing)

        # Bestandsnaam opslaan
        bestandsnaam = f"Waarschuwing_{naam}_{datum}.docx"
        doc.save(bestandsnaam)

        messagebox.showinfo("Succes", f"Brief opgeslagen als {bestandsnaam}")

    except Exception as e:
        messagebox.showerror("Fout", f"Er ging iets mis: {e}")

# GUI bouwen
root = tk.Tk()
root.title("NKZ Waarschuwingsbrief Generator")
root.geometry("400x300")

tk.Label(root, text="Naam bewoner:").pack()
entry_naam = tk.Entry(root, width=40)
entry_naam.pack()

tk.Label(root, text="Kamer:").pack()
entry_kamer = tk.Entry(root, width=40)
entry_kamer.pack()

tk.Label(root, text="Datum waarschuwing (dd-mm-jjjj):").pack()
entry_datum = tk.Entry(root, width=40)
entry_datum.insert(0, datetime.now().strftime("%d-%m-%Y"))
entry_datum.pack()

tk.Label(root, text="Waarschuwing:").pack()
combo_waarschuwing = ttk.Combobox(root, values=["1e", "2e"], state="readonly")
combo_waarschuwing.pack()

tk.Button(root, text="Genereer brief", command=generate_brief).pack(pady=10)

root.mainloop()
