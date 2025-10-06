#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF -> CSV (GUI) z auto-instalacją zależności przy pierwszym uruchomieniu.
- Nie wymaga Pythona u użytkownika (po spakowaniu do EXE).
- Przy pierwszym uruchomieniu dociąga pdfplumber (+zależności) do katalogu użytkownika, bez uprawnień admina.
"""

import os
import sys
import re
import csv
import glob
import threading
import queue
from typing import List, Tuple
import importlib.util

# GUI stdlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ---------- Auto-instalacja zależności (pdfplumber) ----------

def _vendor_dir() -> str:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "PDFtoCSV", "pkgs")
    else:
        return os.path.join(os.path.expanduser("~"), ".local", "share", "PDFtoCSV", "pkgs")

def ensure_runtime_deps():
    """
    Jeżeli brakuje pdfplumber, doinstaluje go (i zależności) lokalnie do katalogu użytkownika.
    """
    target = _vendor_dir()
    os.makedirs(target, exist_ok=True)

    # Dodaj ścieżkę vendor na początek sys.path, żeby import działał po instalacji.
    if target not in sys.path:
        sys.path.insert(0, target)

    need_install = importlib.util.find_spec("pdfplumber") is None
    if not need_install:
        return

    # Spróbuj zasygnalizować użytkownikowi, że będzie jednorazowe pobieranie
    try:
        root = tk.Tk(); root.withdraw()
        messagebox.showinfo("PDF -> CSV", "Trwa jednorazowa instalacja zależności (pdfplumber). Proszę czekać…")
        root.destroy()
    except Exception:
        pass

    try:
        # Bootstrap pip z wbudowanego ensurepip (część standardowej biblioteki)
        import ensurepip
        ensurepip.bootstrap()

        # Wywołaj pip w tym samym procesie
        try:
            from pip._internal.cli.main import main as pipmain
        except Exception:
            try:
                from pip._internal import main as pipmain
            except Exception:
                import pip
                pipmain = getattr(pip, "main", None)

        if pipmain is None:
            raise RuntimeError("pip nie jest dostępny po bootstrapie.")

        # Instalujemy paczki do katalogu --target, bez modyfikacji systemu
        pkgs = [
            "pdfplumber>=0.11"  # pociągnie pdfminer.six i Pillow w wersjach binarnych
        ]
        args = ["install", "--upgrade", "--no-warn-script-location", "--target", target] + pkgs
        rc = pipmain(args)
        if rc != 0:
            raise RuntimeError(f"pip zwrócił kod {rc}")

        # Weryfikacja
        if importlib.util.find_spec("pdfplumber") is None:
            raise RuntimeError("Instalacja zakończona, ale pdfplumber nadal nie jest widoczny w sys.path")

    except Exception as e:
        try:
            root = tk.Tk(); root.withdraw()
            messagebox.showerror(
                "PDF -> CSV",
                f"Nie udało się doinstalować zależności.\n\nPowód: {e}\n\n"
                "Wymagane jest połączenie z internetem przy pierwszym uruchomieniu."
            )
            root.destroy()
        except Exception:
            pass
        raise

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
    # Import pdfplumber dopiero tutaj (po ensure_runtime_deps)
    import pdfplumber

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
            self.root.iconbitmap(default="app.ico")
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
        self.root.after(100, self._poll_queue)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 8}

        frm_in = ttk.LabelFrame(self.root, text="Wejście")
        frm_in.pack(fill="x", **pad)

        ttk.Button(frm_in, text="Wybierz pliki PDF…", command=self._choose_files).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(frm_in, textvariable=self.count_var).grid(row=0, column=1, sticky="w", padx=8)

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
        files = list(self.selected_files)
        if self.selected_folder:
            files += find_pdfs_in_folder(self.selected_folder, recursive=self.recursive_var.get())
        files = list(dict.fromkeys(files))  # dedupe z zachowaniem kolejności

        if not files:
            messagebox.showwarning("Brak plików", "Wybierz co najmniej jeden plik PDF lub folder.")
            return

        out_path = self.output_var.get().strip()
        if not out_path:
            messagebox.showwarning("Brak ścieżki wyjściowej", "Wybierz plik wyjściowy CSV.")
            return

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
            # Upewnij się, że mamy pdfplumber (instalacja jednorazowa)
            ensure_runtime_deps()

            total = len(files)
            all_rows = []
            for i, fpath in enumerate(files, start=1):