#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI do wyciągania tabel z PDF do CSV (pdfplumber).
Uwaga: działa na pdf-ach z tekstem; skany wymagają OCR (np. OCRmyPDF + Tesseract).
"""

import os
import re
import csv
import glob
import threading
import queue
from typing import List, Tuple

import pdfplumber

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ---------- Logika ekstrakcji ----------

def clean_cell(x) -> str:
    if x is None:
        return ""
    s = str(x).replace("\r", " ").replace("\n", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def parse_pages_spec(spec: str, max_pages: int) -> List[int]:
    spec = (spec or "all").strip().lower()
    if spec in ("", "all", "wsz", "wszystkie"):
        return list(range(1, max_pages + 1))
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            try:
                start = int(a); end = int(b)
            except ValueError:
                continue
            if start > end:
                start, end = end, start
            for p in range(start, end + 1):
                if 1 <= p <= max_pages:
                    pages.add(p)
        else:
            try:
                p = int(part)
                if 1 <= p <= max_pages:
                    pages.add(p)
            except ValueError:
                pass
    return sorted(pages)

def extract_tables_from_pdf(pdf_path: str, pages_spec: str = "all") -> List[Tuple[str, int, int, int, List[str]]]:
    """
    Zwraca listę wierszy: (plik, strona, nr_tabeli, nr_wiersza, [komórki...])
    """
    results = []
    with pdfplumber.open(pdf_path) as pdf:
        pages = parse_pages_spec(pages_spec, len(pdf.pages))
        for p in pages:
            page = pdf.pages[p - 1]
            tables = []

            # 1) Strategia linie (gdy tabela ma siatkę)
            try:
                tables = page.extract_tables({
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                })
            except Exception:
                pass

            # 2) Fallback: strategia tekstowa
            if not tables:
                try:
                    tables = page.extract_tables({
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                    })
                except Exception:
                    pass

            for t_idx, table in enumerate(tables or [], start=1):
                if not table:
                    continue
                for r_idx, row in enumerate(table, start=1):
                    if not row:
                        continue
                    cleaned = [clean_cell(c) for c in row]
                    if not any(cleaned):
                        continue
                    results.append((pdf_path, p, t_idx, r_idx, cleaned))
    return results

def find_pdfs_in_folder(folder: str, recursive: bool = True) -> List[str]:
    if not folder:
        return []
    if recursive:
        files = glob.glob(os.path.join(folder, "**", "*.pdf"), recursive=True)
    else:
        files = glob.glob(os.path.join(folder, "*.pdf"))
    return [f for f in files if os.path.isfile(f)]

# ---------- GUI ----------

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF -> CSV (tabele)")
        self.root.geometry("620x360")
        try:
            self.root.iconbitmap(default="app.ico")  # jeśli masz własną ikonę
        except Exception:
            pass

        # Stan
        self.selected_files: List[str] = []
        self.selected_folder: str = ""
        self.log_queue = queue.Queue()

        # Zmienne UI
        self.recursive_var = tk.BooleanVar(value=True)
        self.pages_var = tk.StringVar(value="all")
        self.delimiter_var = tk.StringVar(value=";")
        self.encoding_var = tk.StringVar(value="utf-8-sig")
        self.output_var = tk.StringVar(value=os.path.abspath("output.csv"))
        self.status_var = tk.StringVar(value="Gotowe.")
        self.count_var = tk.StringVar(value="Wybrano 0 plików.")
        self.folder_var = tk.StringVar(value="(brak)")

        self._build_ui()

        # Timer do odbierania logów z wątku
        self.root.after(100, self._poll_queue)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 8}

        frm_in = ttk.LabelFrame(self.root, text="Wejście")
        frm_in.pack(fill="x", **pad)

        # Pliki
        ttk.Button(frm_in, text="Wybierz pliki PDF…", command=self._choose_files).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(frm_in, textvariable=self.count_var).grid(row=0, column=1, sticky="w", padx=8)

        # Folder
        ttk.Button(frm_in, text="Wybierz folder…", command=self._choose_folder).grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(frm_in, textvariable=self.folder_var).grid(row=1, column=1, sticky="w", padx=8)
        ttk.Checkbutton(frm_in, text="Rekurencyjnie", variable=self.recursive_var).grid(row=1, column=2, sticky="w", padx=8)

        frm_opts = ttk.LabelFrame(self.root, text="Opcje")
        frm_opts.pack(fill="x", **pad)
        ttk.Label(frm_opts, text="Strony (np. all, 1,3-5):").grid(row=0, column=0, sticky="e", padx=8, pady=6)
        ttk.Entry(frm_opts, textvariable=self.pages_var, width=18).grid(row=0, column=1, sticky="w")

        ttk.Label(frm_opts, text="Separator CSV:").grid(row=0, column=2, sticky="e", padx=8)
        ttk.Entry(frm_opts, textvariable=self.delimiter_var, width=6).grid(row=0, column=3, sticky="w")

        ttk.Label(frm_opts, text="Kodowanie:").grid(row=0, column=4, sticky="e", padx=8)
        ttk.Combobox(frm_opts, textvariable=self.encoding_var, values=["utf-8-sig", "utf-8", "cp1250"], width=10).grid(row=0, column=5, sticky="w")

        frm_out = ttk.LabelFrame(self.root, text="Wyjście")
        frm_out.pack(fill="x", **pad)
        ttk.Entry(frm_out, textvariable=self.output_var).grid(row=0, column=0, sticky="we", padx=8, pady=6)
        frm_out.columnconfigure(0, weight=1)
        ttk.Button(frm_out, text="Wybierz plik…", command=self._choose_output).grid(row=0, column=1, padx=8)

        frm_run = ttk.Frame(self.root)
        frm_run.pack(fill="x", **pad)
        self.progress = ttk.Progressbar(frm_run, mode="determinate", maximum=100)
        self.progress.grid(row=0, column=0, sticky="we", padx=8)
        frm_run.columnconfigure(0, weight=1)
        ttk.Button(frm_run, text="Start", command=self._start).grid(row=0, column=1, padx=8)

        ttk.Label(self.root, textvariable=self.status_var, foreground="#555").pack(fill="x", padx=14, pady=6)

    def _choose_files(self):
        files = filedialog.askopenfilenames(title="Wybierz pliki PDF", filetypes=[("PDF", "*.pdf")])
        if files:
            # Dołącz i usuń duplikaty, zachowując kolejność
            seen = set(self.selected_files)
            for f in files:
                if f not in seen:
                    self.selected_files.append(f)
                    seen.add(f)
            self.count_var.set(f"Wybrano {len(self.selected_files)} plików.")
            self.status_var.set("Dodano pliki.")

    def _choose_folder(self):
        folder = filedialog.askdirectory(title="Wybierz folder z PDF-ami")
        if folder:
            self.selected_folder = folder
            self.folder_var.set(folder)
            self.status_var.set("Ustawiono folder.")

    def _choose_output(self):
        path = filedialog.asksaveasfilename(
            title="Wybierz plik wyjściowy CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="output.csv",
        )
        if path:
            self.output_var.set(path)

    def _start(self):
        # Zbierz listę wejściowych PDF-ów
        files = list(self.selected_files)
        if self.selected_folder:
            files += find_pdfs_in_folder(self.selected_folder, recursive=self.recursive_var.get())
        # Usuń duplikaty z zachowaniem kolejności
        files = list(dict.fromkeys(files))

        if not files:
            messagebox.showwarning("Brak plików", "Wybierz co najmniej jeden plik PDF lub folder.")
            return

        out_path = self.output_var.get().strip()
        if not out_path:
            messagebox.showwarning("Brak ścieżki wyjściowej", "Wybierz plik wyjściowy CSV.")
            return

        # Zablokuj UI i uruchom wątek
        self._set_controls(False)
        self.status_var.set("Przetwarzanie…")
        self.progress["value"] = 0

        t = threading.Thread(
            target=self._worker,
            args=(files, out_path, self.pages_var.get().strip(), self.delimiter_var.get(), self.encoding_var.get()),
            daemon=True,
        )
        t.start()

    def _worker(self, files: List[str], out_path: str, pages_spec: str, delimiter: str, encoding: str):
        try:
            total = len(files)
            all_rows = []
            for i, fpath in enumerate(files, start=1):
                self.log_queue.put(f"Przetwarzam: {os.path.basename(fpath)} ({i}/{total})")
                try:
                    rows = extract_tables_from_pdf(fpath, pages_spec=pages_spec)
                    all_rows.extend(rows)
                except Exception as e:
                    self.log_queue.put(f"[WARN] {os.path.basename(fpath)}: {e}")

                self.log_queue.put(("progress", int(i * 100 / total)))

            if not all_rows:
                self.log_queue.put("[INFO] Nie wyekstrahowano żadnych tabel.")
                # Mimo to zapisz pusty CSV z nagłówkiem (opcjonalnie)
                header = ["file", "page", "table", "row", "col1"]
                os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
                with open(out_path, "w", newline="", encoding=encoding) as f:
                    csv.writer(f, delimiter=delimiter).writerow(header)
                self.log_queue.put(("done", f"Zapisano pusty CSV (brak danych): {out_path}"))
                return

            max_cols = max((len(r[-1]) for r in all_rows), default=0)
            os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
            with open(out_path, "w", newline="", encoding=encoding) as f:
                writer = csv.writer(f, delimiter=delimiter)
                header = ["file", "page", "table", "row"] + [f"col{i}" for i in range(1, max_cols + 1)]
                writer.writerow(header)
                for (fpath, page, table_idx, row_idx, cells) in all_rows:
                    row = [os.path.basename(fpath), page, table_idx, row_idx] + cells + [""] * (max_cols - len(cells))
                    writer.writerow(row)

            self.log_queue.put(("done", f"OK! Zapisano {len(all_rows)} wierszy do: {out_path}"))
        except Exception as e:
            self.log_queue.put(("error", str(e)))

    def _poll_queue(self):
        try:
            while True:
                item = self.log_queue.get_nowait()
                if isinstance(item, tuple):
                    kind, payload = item
                    if kind == "progress":
                        self.progress["value"] = payload
                    elif kind == "done":
                        self.status_var.set(payload)
                        messagebox.showinfo("Zakończono", payload)
                        self._set_controls(True)
                    elif kind == "error":
                        self.status_var.set(f"Błąd: {payload}")
                        messagebox.showerror("Błąd", payload)
                        self._set_controls(True)
                else:
                    self.status_var.set(str(item))
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)

    def _set_controls(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for child in self.root.winfo_children():
            try:
                child.configure(state=state)
            except tk.TclError:
                # Nie wszystkie widgety mają state bezpośrednio
                for sub in getattr(child, "winfo_children", lambda: [])():
                    try:
                        sub.configure(state=state)
                    except tk.TclError:
                        pass
        # Pasek postępu ma działać zawsze
        self.progress.configure(state="normal")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    App().run()