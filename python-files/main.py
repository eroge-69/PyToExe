
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

def format_field(value):
    if pd.isna(value):
        return ""
    return str(value).replace('"', '').strip()

def format_price(value):
    try:
        return f"{float(value):.4f}"
    except:
        return "0.0000"

def convert_excel_to_epp(excel_path, output_path):
    df = pd.read_excel(excel_path)

    info_fixed = (
        "[INFO]\n"
        "\"1.11\",3,1250,\"Subiekt GT\",\"Tarcopol\",\"Tarcopol-magazyn\",\"TARCOPOL SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ\","
        "\"Starachowice\",\"27-200\",\"Składowa 16\",\"6640000130\",\"01\",\"01\",\"01\",,0,,,"
        "\"Szef\",20250723135804,\"Polska\",\"PL\",\"6640000130\",1\n"
    )

    naglowek_towary = "[NAGLOWEK]\n\"TOWARY\"\n[ZAWARTOSC]\n"
    towary_lines = ""
    cennik_lines = "[NAGLOWEK]\n\"CENNIK\"\n[ZAWARTOSC]\n"

    for _, row in df.iterrows():
        symbol = format_field(row.get("indeks", ""))
        kod = format_field(row.get("kod_producenta", ""))
        nazwa = format_field(row.get("nazwa", ""))
        fiskalna = format_field(row.get("nazwa_fiskalna", ""))
        jm = format_field(row.get("jednostka_nazwa", "")).replace(".", "") + "."
        cena_netto = format_price(row.get("cena_jednostkowa", 0))
        try:
            cena_brutto = f"{float(cena_netto) * 1.23:.4f}"
        except:
            cena_brutto = "0.0000"

        towary_lines += (
            f'1,"{symbol}",,"{kod}","{nazwa}",,"{fiskalna}",,,"{jm}","23",{cena_netto},"23",{cena_netto},0.0000,0.0000,,0,,,,0.0000,0,,,0,"{jm}",0.0000,0.0000,,0,,0,0,,,,,,,,\n'
        )
        cennik_lines += f'"{symbol}","Detaliczna",{cena_netto},{cena_brutto},0.0000,0.0000,0.0000\n'

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(info_fixed + naglowek_towary + towary_lines + cennik_lines)

def run_gui():
    root = tk.Tk()
    root.withdraw()
    excel_path = filedialog.askopenfilename(title="Wybierz plik Excel", filetypes=[("Excel files", "*.xlsx *.xls")])
    if not excel_path:
        return

    output_path = filedialog.asksaveasfilename(defaultextension=".epp", filetypes=[("EPP files", "*.epp")])
    if not output_path:
        return

    try:
        convert_excel_to_epp(excel_path, output_path)
        messagebox.showinfo("Sukces", f"Plik EPP został zapisany:\n{output_path}")
    except Exception as e:
        messagebox.showerror("Błąd", str(e))

if __name__ == "__main__":
    run_gui()
