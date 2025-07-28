#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Programma standalone per estrarre i dati di Trent Film da un PDF,
raggrupparli per titolo, calcolare subtotali e somma totale, e salvare in Excel
attraverso finestre di dialogo per selezione file.
"""

import sys
import pandas as pd
import tabula
import tkinter as tk
from tkinter import filedialog, messagebox

# ======================
# Funzioni di utilità
# ======================
def clean_money(x):
    if isinstance(x, str):
        return float(x.replace(".", "").replace(",", ".").strip())
    return pd.to_numeric(x, errors="coerce")

def main():
    # 1. Finestra per selezionare il PDF
    root = tk.Tk()
    root.withdraw()
    pdf_path = filedialog.askopenfilename(
        title="Seleziona il PDF Cinetel",
        filetypes=[("PDF files", "*.pdf")],
    )
    if not pdf_path:
        messagebox.showwarning("Annullato", "Nessun PDF selezionato, uscita.")
        sys.exit(0)

    # 2. Estrai tutte le tabelle
    try:
        dfs = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True, pandas_options={"dtype": str})
    except Exception as e:
        messagebox.showerror("Errore", f"Fallita lettura PDF:\n{e}")
        sys.exit(1)

    df = pd.concat(dfs, ignore_index=True)
    df.columns = [c.strip() for c in df.columns]

    # 3. Pulizia colonne numeriche
    numeric_cols = ["Incasso (€)", "Spettatori", "Sale"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_money)

    # 4. Filtra solo Trent Film
    mask = df.get("Distributore", "").str.contains("Trent Film", case=False, na=False)
    df_trent = df.loc[mask].copy()
    if df_trent.empty:
        messagebox.showinfo("Nessun dato", "Non sono state trovate righe di Trent Film nel PDF.")
        sys.exit(0)

    # 5. Raggruppa per Titolo e calcola subtotali
    grouped = df_trent.groupby("Titolo")[numeric_cols].sum().reset_index()
    grouped = grouped.sort_values("Incasso (€)", ascending=False)

    # 6. Costruisci DataFrame finale con subtotali e righe originali
    frames = []
    for _, row in grouped.iterrows():
        title = row["Titolo"]
        detail = df_trent[df_trent["Titolo"] == title].copy()
        frames.append(detail)
        subtotal = {col: row[col] for col in numeric_cols}
        subtotal.update({c: "" for c in df_trent.columns if c not in numeric_cols})
        subtotal["Titolo"] = f"Totale {title}"
        frames.append(pd.DataFrame([subtotal]))

    report_df = pd.concat(frames, ignore_index=True)

    # 7. Riga sommatoria generale
    total_vals = report_df[numeric_cols].sum(numeric_only=True).to_dict()
    grand = {col: total_vals[col] for col in numeric_cols}
    grand.update({c: "" for c in df_trent.columns if c not in numeric_cols})
    grand["Titolo"] = "SOMMA TOTALE"
    report_df = pd.concat([report_df, pd.DataFrame([grand])], ignore_index=True)

    # 8. Finestra per selezionare dove salvare l’Excel
    out_path = filedialog.asksaveasfilename(
        title="Salva report Excel",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
    )
    if not out_path:
        messagebox.showwarning("Annullato", "Esportazione annullata.")
        sys.exit(0)

    # 9. Esporta
    try:
        report_df.to_excel(out_path, index=False)
    except Exception as e:
        messagebox.showerror("Errore", f"Fallita esportazione Excel:\n{e}")
        sys.exit(1)

    messagebox.showinfo("Fatto", f"Report salvato con successo:\n{out_path}")

if __name__ == "__main__":
    main()
