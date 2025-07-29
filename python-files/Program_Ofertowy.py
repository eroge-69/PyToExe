
import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from openpyxl import load_workbook, Workbook

# Minimalny szkielet GUI aplikacji
def generate_offer():
    now = datetime.datetime.now()
    offer_number = f"OFR-{now.strftime('%Y%m%d')}-01"
    file_name = f"Oferta_DomyslnaLokalizacja_{now.strftime('%Y%m%d')}_KLIENT.pdf"
    messagebox.showinfo("Generowanie oferty", f"Numer oferty: {offer_number}\nPlik: {file_name}")

root = tk.Tk()
root.title("Program Ofertowy")

tk.Label(root, text="Program Ofertowy – wersja uproszczona").pack(pady=10)
tk.Button(root, text="Generuj ofertę", command=generate_offer).pack(pady=20)

root.geometry("400x150")
root.mainloop()
