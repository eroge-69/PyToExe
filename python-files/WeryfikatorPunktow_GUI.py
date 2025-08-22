#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weryfikator punktów pomiarowych — GUI (Tkinter)

Funkcje:
- Wybór wielu plików Excel (.xlsx, .xls, .xlsm)
- Wybór arkusza i mapowanie kolumn przez listy rozwijane
- Parametry: tolerancja punktów (±), minimalny odstęp między punktami, tolerancja D
- Walidacja:
    * Odstępy: różnica między sąsiednimi punktami (rosnąco) >= min_odstep
    * Tolerancja względem punktów sugerowanych (jeśli podane): |rzeczywisty - sugerowany| <= tolerancja
    * Zgodność D (jeśli podane): |D_zadane - D_pomiar| <= tolerancja_D
- Raport zbiorczy Excel z wynikami dla wszystkich plików + arkusz z błędami szczegółowymi
- Zapis/odczyt konfiguracji JSON (mapowanie kolumn i progi)

Autor: przygotowane przez asystenta AI
"""

import os
import json
import math
import traceback
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

SUPPORTED_EXT = [".xlsx", ".xls", ".xlsm"]


@dataclass
class Config:
    sheet_name: Optional[str] = None
    col_suggested: Optional[str] = None   # kolumna z punktami sugerowanymi (opcjonalna)
    col_actual: Optional[str] = None      # kolumna z punktami rzeczywistymi (wymagana)
    col_D_set: Optional[str] = None       # zadane D (opcjonalne)
    col_D_meas: Optional[str] = None      # zmierzone D (opcjonalne)
    tolerance_points: float = 0.0         # tolerancja ± dla punktów (np. 210 lub 32.5)
    min_spacing: float = 0.0              # minimalny odstęp między punktami (np. 420 lub 65)
    tolerance_D: float = 0.0              # tolerancja ± dla D (np. 0.1 g lub inna)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(s: str) -> "Config":
        data = json.loads(s)
        return Config(**data)


def is_excel(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in SUPPORTED_EXT


def load_sheet_df(path: str, sheet_name: Optional[str]) -> pd.DataFrame:
    try:
        if sheet_name is None:
            # default to first sheet
            xls = pd.ExcelFile(path)
            sheet_name = xls.sheet_names[0]
        df = pd.read_excel(path, sheet_name=sheet_name, engine=None)
        return df
    except Exception:
        # Fallback to openpyxl for xlsx/xlsm
        try:
            df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
            return df
        except Exception as e:
            raise e


def coerce_numeric(series: pd.Series) -> pd.Series:
    # Zamień przecinki na kropki, usuń spacje, konwertuj na float
    return pd.to_numeric(series.astype(str).str.replace(",", ".", regex=False).str.strip(), errors="coerce")


def validate_points(df: pd.DataFrame, cfg: Config) -> Dict[str, Any]:
    """
    Zwraca słownik z kluczami:
    - passed (bool)
    - errors (List[str])
    - details (DataFrame) – wierszowe wyniki porównań
    - info (Dict) – pomocnicze informacje
    """
    errors: List[str] = []

    # Sprawdź obecność wymaganej kolumny
    if cfg.col_actual is None or cfg.col_actual not in df.columns:
        raise ValueError("Brak poprawnej kolumny z punktami rzeczywistymi (col_actual).")

    actual = coerce_numeric(df[cfg.col_actual])

    suggested = None
    if cfg.col_suggested and cfg.col_suggested in df.columns:
        suggested = coerce_numeric(df[cfg.col_suggested])

    D_set = coerce_numeric(df[cfg.col_D_set]) if cfg.col_D_set and cfg.col_D_set in df.columns else None
    D_meas = coerce_numeric(df[cfg.col_D_meas]) if cfg.col_D_meas and cfg.col_D_meas in df.columns else None

    # Zbuduj tabelę wyników szczegółowych (tylko niepuste wartości punktów)
    res_rows = []
    # Wiersze, gdzie actual nie jest NaN
    idx_valid = actual.dropna().index.tolist()

    # --- Sprawdzanie tolerancji punktów względem sugerowanych ---
    if suggested is not None:
        for i in idx_valid:
            a = actual.loc[i]
            s = suggested.loc[i] if i in suggested.index else math.nan
            if pd.notna(s):
                diff = abs(a - s)
                ok = (diff <= cfg.tolerance_points)
                if not ok:
                    errors.append(f"Rząd {i+2}: punkt {a} vs sugerowany {s} — różnica {diff:.6g} > ±{cfg.tolerance_points}")
                res_rows.append({
                    "row": i+2,  # +2: 1 dla indeksu 1-based, 1 dla nagłówka
                    "actual": a,
                    "suggested": s,
                    "diff_points": diff,
                    "points_ok": ok
                })
            else:
                # brak sugerowanego – tylko zapis
                res_rows.append({
                    "row": i+2,
                    "actual": a,
                    "suggested": None,
                    "diff_points": None,
                    "points_ok": True if suggested is None else None
                })
    else:
        # Bez sugerowanych – tylko zapis actual
        for i in idx_valid:
            a = actual.loc[i]
            res_rows.append({
                "row": i+2,
                "actual": a,
                "suggested": None,
                "diff_points": None,
                "points_ok": True
            })

    # --- Sprawdzanie odstępów ---
    actual_sorted = sorted([float(x) for x in actual.dropna().tolist()])
    for j in range(len(actual_sorted)-1):
        d = actual_sorted[j+1] - actual_sorted[j]
        if d < cfg.min_spacing:
            errors.append(f"Odstęp {actual_sorted[j]} → {actual_sorted[j+1]} = {d:.6g} < {cfg.min_spacing}")
    # Dodaj info o parach odstępów
    spacing_info = [{"A": actual_sorted[j], "B": actual_sorted[j+1], "diff": actual_sorted[j+1]-actual_sorted[j],
                     "spacing_ok": (actual_sorted[j+1]-actual_sorted[j]) >= cfg.min_spacing}
                    for j in range(len(actual_sorted)-1)]

    # --- Sprawdzanie D ---
    D_rows = []
    if D_set is not None and D_meas is not None:
        # Porównuj wiersz do wiersza, tylko tam gdzie oba nie NaN
        common_idx = [i for i in df.index if pd.notna(D_set.loc[i]) and pd.notna(D_meas.loc[i])]
        for i in common_idx:
            ds = float(D_set.loc[i])
            dm = float(D_meas.loc[i])
            diff = abs(ds - dm)
            ok = diff <= cfg.tolerance_D
            if not ok:
                errors.append(f"D (rząd {i+2}): zadane {ds} vs pomiar {dm} — różnica {diff:.6g} > ±{cfg.tolerance_D}")
            D_rows.append({"row": i+2, "D_set": ds, "D_meas": dm, "diff_D": diff, "D_ok": ok})

    details_df = pd.DataFrame(res_rows)
    spacing_df = pd.DataFrame(spacing_info)
    D_df = pd.DataFrame(D_rows)

    passed = (len(errors) == 0)
    return {
        "passed": passed,
        "errors": errors,
        "details": details_df,
        "spacing": spacing_df,
        "Dcheck": D_df,
        "info": {
            "n_points": len(actual_sorted),
            "min_spacing": cfg.min_spacing,
            "tolerance_points": cfg.tolerance_points,
            "tolerance_D": cfg.tolerance_D
        }
    }


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weryfikator punktów pomiarowych")
        self.geometry("920x620")

        self.files: List[str] = []
        self.df_preview: Optional[pd.DataFrame] = None
        self.config = Config()

        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)

        # --- Sekcja plików ---
        files_frame = ttk.LabelFrame(frm, text="Pliki")
        files_frame.pack(fill="x", pady=5)

        ttk.Button(files_frame, text="Dodaj pliki…", command=self.add_files).pack(side="left", padx=5, pady=5)
        ttk.Button(files_frame, text="Wyczyść", command=self.clear_files).pack(side="left", padx=5, pady=5)
        self.files_var = tk.StringVar(value="(brak plików)")
        ttk.Label(files_frame, textvariable=self.files_var).pack(side="left", padx=10, pady=5)

        # --- Sekcja konfiguracji ---
        cfg_frame = ttk.LabelFrame(frm, text="Konfiguracja (arkusz i kolumny)")
        cfg_frame.pack(fill="x", pady=5)

        # Arkusz
        ttk.Label(cfg_frame, text="Arkusz:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        self.sheet_cb = ttk.Combobox(cfg_frame, values=[], state="readonly")
        self.sheet_cb.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
        self.sheet_cb.bind("<<ComboboxSelected>>", self.on_sheet_change)

        # Kolumny
        ttk.Label(cfg_frame, text="Punkty sugerowane (opcjonalnie):").grid(row=1, column=0, sticky="w", padx=5, pady=4)
        self.col_suggested_cb = ttk.Combobox(cfg_frame, values=[], state="readonly")
        self.col_suggested_cb.grid(row=1, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(cfg_frame, text="Punkty rzeczywiste:").grid(row=2, column=0, sticky="w", padx=5, pady=4)
        self.col_actual_cb = ttk.Combobox(cfg_frame, values=[], state="readonly")
        self.col_actual_cb.grid(row=2, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(cfg_frame, text="D (zadane) – opcjonalnie:").grid(row=3, column=0, sticky="w", padx=5, pady=4)
        self.col_D_set_cb = ttk.Combobox(cfg_frame, values=[], state="readonly")
        self.col_D_set_cb.grid(row=3, column=1, sticky="ew", padx=5, pady=4)

        ttk.Label(cfg_frame, text="D (pomiar) – opcjonalnie:").grid(row=4, column=0, sticky="w", padx=5, pady=4)
        self.col_D_meas_cb = ttk.Combobox(cfg_frame, values=[], state="readonly")
        self.col_D_meas_cb.grid(row=4, column=1, sticky="ew", padx=5, pady=4)

        cfg_frame.columnconfigure(1, weight=1)

        # --- Parametry ---
        params = ttk.LabelFrame(frm, text="Parametry walidacji")
        params.pack(fill="x", pady=5)

        self.tol_points_var = tk.StringVar(value="0")
        self.min_spacing_var = tk.StringVar(value="0")
        self.tol_D_var = tk.StringVar(value="0")

        ttk.Label(params, text="Tolerancja punktów ± [g]:").grid(row=0, column=0, sticky="w", padx=5, pady=4)
        ttk.Entry(params, textvariable=self.tol_points_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=4)

        ttk.Label(params, text="Minimalny odstęp [g]:").grid(row=0, column=2, sticky="w", padx=5, pady=4)
        ttk.Entry(params, textvariable=self.min_spacing_var, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=4)

        ttk.Label(params, text="Tolerancja D ± [g]:").grid(row=0, column=4, sticky="w", padx=5, pady=4)
        ttk.Entry(params, textvariable=self.tol_D_var, width=10).grid(row=0, column=5, sticky="w", padx=5, pady=4)

        # --- Przyciski akcji ---
        actions = ttk.Frame(frm)
        actions.pack(fill="x", pady=8)
        ttk.Button(actions, text="Załaduj strukturę z pierwszego pliku", command=self.load_first_file_structure).pack(side="left", padx=5)
        ttk.Button(actions, text="Analizuj i wygeneruj raport", command=self.run_analysis).pack(side="left", padx=5)
        ttk.Button(actions, text="Zapisz konfigurację…", command=self.save_config).pack(side="left", padx=5)
        ttk.Button(actions, text="Wczytaj konfigurację…", command=self.load_config).pack(side="left", padx=5)

        # --- Podgląd statusu ---
        self.status_var = tk.StringVar(value="Gotowy.")
        ttk.Label(frm, textvariable=self.status_var, anchor="w").pack(fill="x", pady=5)

        # --- Podgląd przykładowych danych ---
        self.preview = ttk.Treeview(frm, columns=[], show="headings", height=10)
        self.preview.pack(fill="both", expand=True, pady=6)

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Wybierz pliki Excel", filetypes=[("Excel", "*.xlsx *.xls *.xlsm")])
        if not paths:
            return
        self.files.extend([p for p in paths if is_excel(p)])
        self.files = list(dict.fromkeys(self.files))  # unikaj duplikatów
        self.files_var.set(f"{len(self.files)} plik(ów) wybranych")

    def clear_files(self):
        self.files = []
        self.files_var.set("(brak plików)")

    def load_first_file_structure(self):
        if not self.files:
            messagebox.showwarning("Uwaga", "Najpierw dodaj przynajmniej jeden plik.")
            return
        first = self.files[0]
        try:
            xls = pd.ExcelFile(first)
            self.sheet_cb["values"] = xls.sheet_names
            # automatycznie wybierz arkusz o nazwie sugerującej punkty
            preferred = None
            for name in xls.sheet_names:
                low = name.lower()
                if "punkt" in low or "pomiaro" in low or "ocena" in low:
                    preferred = name
                    break
            self.sheet_cb.set(preferred or xls.sheet_names[0])
            self.on_sheet_change()
            self.status_var.set(f"Załadowano strukturę z: {os.path.basename(first)}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się odczytać pliku:\n{e}")

    def on_sheet_change(self, event=None):
        if not self.files:
            return
        sheet = self.sheet_cb.get()
        if not sheet:
            return
        try:
            df = load_sheet_df(self.files[0], sheet)
            self.df_preview = df

            columns = list(map(str, df.columns))
            for cb in [self.col_suggested_cb, self.col_actual_cb, self.col_D_set_cb, self.col_D_meas_cb]:
                cb["values"] = columns
                # auto-guess
                guess = None
                cname_lower = [c.lower() for c in columns]
                if cb is self.col_actual_cb:
                    for key in ["obciążenie_sort", "obciazenie_sort", "punkt", "punkty", "rzeczyw", "actual"]:
                        for c in columns:
                            if key in c.lower():
                                guess = c; break
                        if guess: break
                elif cb is self.col_suggested_cb:
                    for key in ["obciążenie_onelab", "obciazenie_onelab", "suger", "nominal", "target", "zadane"]:
                        for c in columns:
                            if key in c.lower():
                                guess = c; break
                        if guess: break
                elif cb is self.col_D_set_cb:
                    for key in ["d", "zadane", "set"]:
                        for c in columns:
                            if key == "d":
                                # prefer exact 'D' column name
                                for c2 in columns:
                                    if c2.strip().lower() == "d":
                                        guess = c2; break
                                if guess: break
                            if key in c.lower():
                                guess = c; break
                        if guess: break
                elif cb is self.col_D_meas_cb:
                    for key in ["pomiar", "meas", "zmierzone", "wynik"]:
                        for c in columns:
                            if key in c.lower():
                                guess = c; break
                        if guess: break
                if guess:
                    cb.set(guess)

            # update preview tree
            self.preview.delete(*self.preview.get_children())
            self.preview["columns"] = columns[:10]  # ogranicz do 10 kolumn w podglądzie
            for c in self.preview["columns"]:
                self.preview.heading(c, text=c)
                self.preview.column(c, width=150, anchor="w")
            for _, row in df.iloc[:50, :10].iterrows():
                vals = [str(row[c]) for c in self.preview["columns"]]
                self.preview.insert("", "end", values=vals)

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Błąd", f"Nie udało się wczytać arkusza '{sheet}':\n{e}")

    def gather_config(self) -> Optional[Config]:
        try:
            tol_points = float(str(self.tol_points_var.get()).replace(",", "."))
            min_spacing = float(str(self.min_spacing_var.get()).replace(",", "."))
            tol_D = float(str(self.tol_D_var.get()).replace(",", "."))
        except ValueError:
            messagebox.showerror("Błąd", "Parametry tolerancji/odstępu muszą być liczbami.")
            return None

        cfg = Config(
            sheet_name=self.sheet_cb.get() or None,
            col_suggested=self.col_suggested_cb.get() or None,
            col_actual=self.col_actual_cb.get() or None,
            col_D_set=self.col_D_set_cb.get() or None,
            col_D_meas=self.col_D_meas_cb.get() or None,
            tolerance_points=tol_points,
            min_spacing=min_spacing,
            tolerance_D=tol_D,
        )
        if not cfg.col_actual:
            messagebox.showerror("Błąd", "Wybierz kolumnę 'Punkty rzeczywiste'.")
            return None
        return cfg

    def run_analysis(self):
        if not self.files:
            messagebox.showwarning("Uwaga", "Dodaj pliki do analizy.")
            return
        cfg = self.gather_config()
        if not cfg:
            return

        all_results = []
        details_rows = []
        spacing_rows = []
        D_rows = []

        for path in self.files:
            try:
                df = load_sheet_df(path, cfg.sheet_name)
                result = validate_points(df, cfg)

                status = "PASS" if result["passed"] else "FAIL"
                all_results.append({
                    "Plik": os.path.basename(path),
                    "Arkusz": cfg.sheet_name,
                    "Status": status,
                    "Liczba punktów": result["info"]["n_points"],
                    "Uwagi": "; ".join(result["errors"]) if result["errors"] else ""
                })

                # Szczegóły — dodaj nazwę pliku do każdej linijki
                if not result["details"].empty:
                    tmp = result["details"].copy()
                    tmp.insert(0, "Plik", os.path.basename(path))
                    details_rows.append(tmp)

                if not result["spacing"].empty:
                    tmp = result["spacing"].copy()
                    tmp.insert(0, "Plik", os.path.basename(path))
                    spacing_rows.append(tmp)

                if not result["Dcheck"].empty:
                    tmp = result["Dcheck"].copy()
                    tmp.insert(0, "Plik", os.path.basename(path))
                    D_rows.append(tmp)

            except Exception as e:
                all_results.append({
                    "Plik": os.path.basename(path),
                    "Arkusz": cfg.sheet_name,
                    "Status": "ERROR",
                    "Liczba punktów": 0,
                    "Uwagi": f"Błąd: {e}"
                })

        summary_df = pd.DataFrame(all_results)
        details_df = pd.concat(details_rows, ignore_index=True) if details_rows else pd.DataFrame()
        spacing_df = pd.concat(spacing_rows, ignore_index=True) if spacing_rows else pd.DataFrame()
        D_df = pd.concat(D_rows, ignore_index=True) if D_rows else pd.DataFrame()

        # Zapis raportu
        out_path = filedialog.asksaveasfilename(
            title="Zapisz raport Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        if not out_path:
            return

        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            summary_df.to_excel(writer, sheet_name="PODSUMOWANIE", index=False)
            if not details_df.empty:
                details_df.to_excel(writer, sheet_name="PUNKTY_vs_SUG", index=False)
            if not spacing_df.empty:
                spacing_df.to_excel(writer, sheet_name="ODSTEPY", index=False)
            if not D_df.empty:
                D_df.to_excel(writer, sheet_name="D_CHECK", index=False)

        messagebox.showinfo("Gotowe", f"Raport zapisany:\n{out_path}")

    def save_config(self):
        cfg = self.gather_config()
        if not cfg:
            return
        path = filedialog.asksaveasfilename(
            title="Zapisz konfigurację",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(cfg.to_json())
        messagebox.showinfo("Zapisano", f"Konfiguracja zapisana do:\n{path}")

    def load_config(self):
        path = filedialog.askopenfilename(
            title="Wczytaj konfigurację",
            filetypes=[("JSON", "*.json")]
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = Config.from_json(f.read())
            self.config = cfg
            # Ustaw UI
            if self.files:
                xls = pd.ExcelFile(self.files[0])
                self.sheet_cb["values"] = xls.sheet_names
            if cfg.sheet_name:
                self.sheet_cb.set(cfg.sheet_name)
                self.on_sheet_change()
            if cfg.col_suggested: self.col_suggested_cb.set(cfg.col_suggested)
            if cfg.col_actual: self.col_actual_cb.set(cfg.col_actual)
            if cfg.col_D_set: self.col_D_set_cb.set(cfg.col_D_set)
            if cfg.col_D_meas: self.col_D_meas_cb.set(cfg.col_D_meas)
            self.tol_points_var.set(str(cfg.tolerance_points))
            self.min_spacing_var.set(str(cfg.min_spacing))
            self.tol_D_var.set(str(cfg.tolerance_D))
            messagebox.showinfo("Wczytano", "Konfiguracja została wczytana.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wczytać konfiguracji:\n{e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
