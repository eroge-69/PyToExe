#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import csv
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Tuple
import pdfplumber

# --- Logika z poprzedniego skryptu (bez zmian) ---
def clean_cell(x) -> str:
    if x is None: return ""
    s = str(x).replace("\r", " ").replace("\n", " ").strip()
    return re.sub(r"\s+", " ", s)

def extract_tables_from_pdf(pdf_path: str) -> List[Tuple[str, int, int, int, List[str]]]:
    """Zwraca listę wierszy: (plik, strona, nr_tabeli, nr_wiersza, [komórki...])"""
    results = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                # Próbuj obu strategii, wybierz tę, która dała więcej danych
                tables_lines = page.extract_tables({"vertical_strategy": "lines", "horizontal_strategy": "lines"})
                tables_text = page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})
                
                # Prosta heurystyka: weź wynik z większą liczbą komórek
                cells_lines = sum(len(row) for tbl in tables_lines for row in tbl)
                cells_text = sum(len(row) for tbl in tables_text for row in tbl)
                tables = tables_lines if cells_lines >= cells_text else tables_text
                
                for t_idx, table in enumerate(tables, 1):
                    if not table: continue
                    for r_idx, row in enumerate(table, 1):
                        if not row: continue
                        cleaned = [clean_cell(c) for c in row]
                        if not any(cleaned): continue
                        results.append((os.path.basename(pdf_path), i, t_idx, r_idx, cleaned))
    except Exception as e:
        print(f"[BŁĄD] Nie udało się przetworzyć {pdf_path}: {e}")
    return results

# --- Klasa aplikacji GUI ---
class PdfExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ekstraktor Tabel z PDF do CSV")
        self.root.geometry("500x250")
        
        self.input_paths = []
        self.output_path = ""
        
        # Styl
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")

        # Ramka główna
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Wybór plików wejściowych
        self.btn_select_files = ttk.Button(main_frame, text="1. Wybierz pliki PDF...", command=self.select_input_files)
        self.btn_select_files.pack(fill=tk.X, pady=5)
        self.lbl_input_files = ttk.Label(main_frame, text="Nie wybrano plików", wraplength=480)
        self.lbl_input_files.pack(fill=tk.X)

        # 2. Wybór pliku wyjściowego
        self.btn_select_output = ttk.Button(main_frame, text="2. Wybierz gdzie zapisać CSV...", command=self.select_output_file)
        self.btn_select_output.pack(fill=tk.X, pady=5)
        self.lbl_output_file = ttk.Label(main_frame, text="Nie wybrano pliku wyjściowego", wraplength=480)
        self.lbl_output_file.pack(fill=tk.X)

        # 3. Przycisk start
        self.btn_start = ttk.Button(main_frame, text="3. Uruchom ekstrakcję", command=self.start_processing)
        self.btn_start.pack(fill=tk.X, pady=20)
        
        # Pasek statusu
        self.status_var = tk.StringVar()
        self.status_var.set("Gotowy.")
        self.status_label = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=5)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def select_input_files(self):
        files = filedialog.askopenfilenames(
            title="Wybierz pliki PDF",
            filetypes=[("Pliki PDF", "*.pdf"), ("Wszystkie pliki", "*.*")]
        )
        if files:
            self.input_paths = list(files)
            self.lbl_input_files.config(text=f"Wybrano {len(self.input_paths)} plików.")

    def select_output_file(self):
        file = filedialog.asksaveasfilename(
            title="Zapisz jako...",
            defaultextension=".csv",
            filetypes=[("Plik CSV", "*.csv")]
        )
        if file:
            self.output_path = file
            self.lbl_output_file.config(text=os.path.basename(file))
            
    def start_processing(self):
        if not self.input_paths:
            messagebox.showerror("Błąd", "Proszę wybrać przynajmniej jeden plik PDF.")
            return
        if not self.output_path:
            messagebox.showerror("Błąd", "Proszę wybrać ścieżkę do zapisu pliku CSV.")
            return

        self.set_ui_state(tk.DISABLED)
        self.status_var.set("Przetwarzanie...")

        # Uruchomienie przetwarzania w osobnym wątku, aby nie blokować GUI
        thread = threading.Thread(target=self.processing_worker)
        thread.start()

    def set_ui_state(self, state):
        self.btn_select_files.config(state=state)
        self.btn_select_output.config(state=state)
        self.btn_start.config(state=state)

    def processing_worker(self):
        all_rows = []
        for fpath in self.input_paths:
            self.status_var.set(f"Przetwarzanie: {os.path.basename(fpath)}...")
            rows = extract_tables_from_pdf(fpath)
            all_rows.extend(rows)
        
        if not all_rows:
            messagebox.showwarning("Informacja", "Nie znaleziono żadnych tabel w wybranych plikach.")
            self.status_var.set("Gotowy. Nie znaleziono tabel.")
            self.set_ui_state(tk.NORMAL)
            return
            
        max_cols = max((len(r[-1]) for r in all_rows), default=0)
        
        try:
            with open(self.output_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                header = ["plik", "strona", "tabela_nr", "wiersz_nr"] + [f"kolumna_{i}" for i in range(1, max_cols + 1)]
                writer.writerow(header)

                for (fpath_base, page, tbl_idx, row_idx, cells) in all_rows:
                    row = [fpath_base, page, tbl_idx, row_idx] + cells + [""] * (max_cols - len(cells))
                    writer.writerow(row)
            
            self.status_var.set(f"Zakończono! Zapisano {len(all_rows)} wierszy.")
            messagebox.showinfo("Sukces", f"Pomyślnie zapisano dane do pliku:\n{self.output_path}")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać pliku CSV:\n{e}")
            self.status_var.set("Błąd zapisu pliku.")
        
        self.set_ui_state(tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = PdfExtractorApp(root)
    root.mainloop()