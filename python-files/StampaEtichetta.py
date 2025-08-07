
import tkinter as tk
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import tempfile
import os
import win32print
import win32api

def stampa_etichetta(nome, cognome, data_nascita):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, "etichetta.pdf")
    width, height = 5 * cm, 3 * cm

    c = canvas.Canvas(file_path, pagesize=(width, height))
    c.setFont("Helvetica", 10)
    c.drawString(10, height - 20, f"Nome: {nome}")
    c.drawString(10, height - 35, f"Cognome: {cognome}")
    c.drawString(10, height - 50, f"Data di nascita: {data_nascita}")
    c.showPage()
    c.save()

    # Manda alla stampante predefinita
    win32api.ShellExecute(
        0,
        "print",
        file_path,
        None,
        ".",
        0
    )

def invia():
    nome = entry_nome.get()
    cognome = entry_cognome.get()
    data = entry_data.get()

    if not nome or not cognome or not data:
        messagebox.showerror("Errore", "Compila tutti i campi.")
        return

    try:
        stampa_etichetta(nome, cognome, data)
        messagebox.showinfo("Stampato", "Etichetta stampata con successo!")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nella stampa: {e}")

# Interfaccia
finestra = tk.Tk()
finestra.title("StampaEtichetta")

tk.Label(finestra, text="Nome").grid(row=0, column=0, padx=5, pady=5)
entry_nome = tk.Entry(finestra)
entry_nome.grid(row=0, column=1)

tk.Label(finestra, text="Cognome").grid(row=1, column=0, padx=5, pady=5)
entry_cognome = tk.Entry(finestra)
entry_cognome.grid(row=1, column=1)

tk.Label(finestra, text="Data di nascita").grid(row=2, column=0, padx=5, pady=5)
entry_data = tk.Entry(finestra)
entry_data.grid(row=2, column=1)

tk.Button(finestra, text="Stampa Etichetta", command=invia).grid(row=3, column=0, columnspan=2, pady=10)

finestra.mainloop()
