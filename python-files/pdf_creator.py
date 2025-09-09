# Rechnungs-Generator mit GUI und Unicode-Unterstützung
import datetime
from fpdf import FPDF
import tkinter as tk
from tkinter import messagebox, simpledialog
import os

FONT_PATH = "DejaVuSans.ttf"  # Lade die TTF-Datei ins gleiche Verzeichnis wie dein Skript


# --- PDF-Funktion ---
def erstelle_rechnung(kunde, adresse, produkte):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
    pdf.add_font("DejaVu", "B", FONT_PATH, uni=True)

    pdf.set_font("DejaVu", "B", 16)
    pdf.cell(200, 10, "RECHNUNG", ln=True, align='C')

    pdf.set_font("DejaVu", "", 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Kunde: {kunde}", ln=True)
    pdf.cell(200, 10, f"Adresse: {adresse}", ln=True)
    pdf.cell(200, 10, f"Datum: {datetime.date.today()}", ln=True)
    pdf.ln(10)

    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(80, 10, "Produkt", border=1)
    pdf.cell(30, 10, "Menge", border=1, align='C')
    pdf.cell(40, 10, "Preis/Stück (€)", border=1, align='C')
    pdf.cell(40, 10, "Gesamt (€)", border=1, align='C')
    pdf.ln()

    pdf.set_font("DejaVu", "", 12)
    gesamt_summe = 0
    for produkt, menge, preis in produkte:
        gesamt = menge * preis
        gesamt_summe += gesamt
        pdf.cell(80, 10, produkt, border=1)
        pdf.cell(30, 10, str(menge), border=1, align='C')
        pdf.cell(40, 10, f"{preis:.2f} €", border=1, align='C')
        pdf.cell(40, 10, f"{gesamt:.2f} €", border=1, align='C')
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(150, 10, "GESAMT:", align='R')
    pdf.cell(40, 10, f"{gesamt_summe:.2f} €", border=1, align='C')

    dateiname = f"Rechnung_{kunde.replace(' ', '_')}_{datetime.date.today()}.pdf"
    pdf.output(dateiname)
    messagebox.showinfo("Fertig", f"Rechnung erstellt: {dateiname}")


# --- GUI ---
def add_produkt():
    produkt_name = simpledialog.askstring("Produkt", "Produktname eingeben:")
    if not produkt_name:
        return
    menge = simpledialog.askinteger("Menge", f"Menge von {produkt_name}:")
    if menge is None:
        return
    preis = simpledialog.askfloat("Preis", f"Preis pro Stück von {produkt_name} (€):")
    if preis is None:
        return
    produkte.append((produkt_name, menge, preis))
    listbox_produkte.insert(tk.END, f"{produkt_name} | {menge} Stück | {preis:.2f} €/Stück")


def generiere_rechnung():
    kunde = entry_kunde.get()
    adresse = entry_adresse.get()
    if not kunde or not adresse:
        messagebox.showerror("Fehler", "Bitte Kunde und Adresse ausfüllen!")
        return
    if not produkte:
        messagebox.showerror("Fehler", "Bitte mindestens ein Produkt hinzufügen!")
        return
    erstelle_rechnung(kunde, adresse, produkte)


# --- Hauptfenster ---
root = tk.Tk()
root.title("Rechnungs-Generator")

produkte = []

tk.Label(root, text="Kunde:").grid(row=0, column=0, sticky='e')
entry_kunde = tk.Entry(root, width=40)
entry_kunde.grid(row=0, column=1, padx=5, pady=5)

tk.Label(root, text="Adresse:").grid(row=1, column=0, sticky='e')
entry_adresse = tk.Entry(root, width=40)
entry_adresse.grid(row=1, column=1, padx=5, pady=5)

tk.Button(root, text="Produkt hinzufügen", command=add_produkt).grid(row=2, column=0, columnspan=2, pady=5)

listbox_produkte = tk.Listbox(root, width=60)
listbox_produkte.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

tk.Button(root, text="Rechnung erstellen", command=generiere_rechnung, bg='green', fg='white').grid(row=4, column=0,
                                                                                                    columnspan=2,
                                                                                                    pady=10)

root.mainloop()
