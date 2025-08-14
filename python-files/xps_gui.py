#!/usr/bin/env python3
# XPS Batch Extractor GUI
# Author: ChatGPT
# Description: Select Excel files, choose elements (Li, O, F, C, Si, S), and export tab-delimited .txt files.
# - Finds the "eV" and "Counts / s" columns automatically (no header/index in output)
# - Formats numbers to a specified number of decimal places (default 8)
# - Optionally appends " .arx -xy" after .txt (disabled by default)
# - Optionally zip results after export

import os
import sys
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from typing import List, Tuple, Optional

# -------------------------- Helpers --------------------------

DEFAULT_SHEETS = {
    "C": "C1s Scan",
    "O": "O1s Scan",
    "F": "F1s Scan",
    "S": "S2p Scan",
    "Si": "Si2p Scan",
    "Li": "Li1s Scan",
}

def guess_header_row_and_cols(df: pd.DataFrame) -> Optional[Tuple[int, int, int]]:
    """
    Try to find the row index of the header (where 'eV' and 'Counts / s' occur),
    and return (data_start_idx, ev_col, counts_col).
    Returns None if not found.
    """
    # Work with string versions to avoid NaN issues
    for r in range(min(len(df), 200)):
        row_vals = [str(v).strip() if pd.notna(v) else "" for v in df.iloc[r].tolist()]
        # Look for 'eV' and 'Counts / s' in the same row
        try:
            ev_idx = row_vals.index("eV")
        except ValueError:
            ev_idx = -1
        try:
            cnt_idx = row_vals.index("Counts / s")
        except ValueError:
            cnt_idx = -1

        if ev_idx != -1 and cnt_idx != -1:
            # Data likely starts on next row
            return (r + 1, ev_idx, cnt_idx)

    # Fallback heuristic like earlier (row 17, cols 0 and 2) if present
    if df.shape[1] >= 3 and len(df) > 18:
        # Check row 17 for 'eV' in col 0 and 'Counts / s' in col 2
        row17 = [str(v).strip() if pd.notna(v) else "" for v in df.iloc[17].tolist()]
        if (len(row17) > 2 and row17[0] == "eV" and row17[2] == "Counts / s"):
            return (18, 0, 2)

    return None

def read_sheet_extract(path: str, sheet_name: str, decimals: int) -> Optional[pd.DataFrame]:
    """
    Read a sheet and extract [eV, Counts / s] as formatted strings with specified decimals.
    Returns DataFrame with two columns (strings). None if extraction fails.
    """
    try:
        # Try reading with default engine (openpyxl for .xlsx). For .xls, pandas may need xlrd.
        xls = pd.ExcelFile(path)
        if sheet_name not in xls.sheet_names:
            return None
        df_raw = xls.parse(sheet_name, header=None)

        header_info = guess_header_row_and_cols(df_raw)
        if header_info is None:
            return None

        start_idx, ev_col, cnt_col = header_info
        sub = df_raw.iloc[start_idx:, [ev_col, cnt_col]].copy()
        sub.columns = ["eV", "Counts / s"]
        sub = sub.dropna(subset=["eV", "Counts / s"])

        # Remove stray header strings
        sub = sub[(sub["eV"].astype(str).str.strip() != "eV") & (sub["Counts / s"].astype(str).str.strip() != "Counts / s")]

        # Convert to floats, then format
        sub["eV"] = pd.to_numeric(sub["eV"], errors="coerce")
        sub["Counts / s"] = pd.to_numeric(sub["Counts / s"], errors="coerce")
        sub = sub.dropna(subset=["eV", "Counts / s"])

        fmt = "{:." + str(decimals) + "f}"
        sub["eV"] = sub["eV"].map(lambda x: fmt.format(float(x)))
        sub["Counts / s"] = sub["Counts / s"].map(lambda x: fmt.format(float(x)))

        return sub[["eV", "Counts / s"]]
    except Exception:
        traceback.print_exc()
        return None

def export_txt(df: pd.DataFrame, out_path: str, delimiter: str = "\t"):
    df.to_csv(out_path, sep=delimiter, index=False, header=False)

# -------------------------- GUI --------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("XPS Batch Extractor")
        self.geometry("860x620")
        self.minsize(820, 560)

        # State
        self.files: List[str] = []
        self.decimals_var = tk.IntVar(value=8)
        self.append_arx_var = tk.BooleanVar(value=False)
        self.zip_var = tk.BooleanVar(value=True)

        self.delim_var = tk.StringVar(value="\\t")
        self.outdir_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "XPS_exports"))

        # Elements (checkboxes)
        self.element_vars = {
            key: tk.BooleanVar(value=False) for key in DEFAULT_SHEETS.keys()
        }
        # Default to Li, O, F as examples checked?
        for k in ["Li", "O", "F"]:
            if k in self.element_vars:
                self.element_vars[k].set(True)

        # Custom sheet names input (comma-separated)
        self.custom_sheets_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        # Top: file selection
        top = ttk.LabelFrame(self, text="Files")
        top.pack(fill="x", padx=10, pady=10)

        btn_frame = ttk.Frame(top)
        btn_frame.pack(fill="x", padx=10, pady=6)
        ttk.Button(btn_frame, text="Add Files (.xlsx/.xls)", command=self.add_files).pack(side="left")
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected).pack(side="left", padx=8)
        ttk.Button(btn_frame, text="Clear", command=self.clear_files).pack(side="left")

        self.file_list = tk.Listbox(top, selectmode=tk.EXTENDED, height=7)
        self.file_list.pack(fill="both", expand=True, padx=10, pady=6)

        # Middle: options
        opt = ttk.LabelFrame(self, text="Options")
        opt.pack(fill="x", padx=10, pady=8)

        # Elements
        elem_box = ttk.LabelFrame(opt, text="Elements to extract")
        elem_box.pack(side="left", padx=10, pady=8, fill="both", expand=True)

        elem_grid = ttk.Frame(elem_box)
        elem_grid.pack(fill="x", padx=10, pady=5)

        col = 0
        row = 0
        for key, sheet in DEFAULT_SHEETS.items():
            cb = ttk.Checkbutton(elem_grid, text=f"{key} ({sheet})", variable=self.element_vars[key])
            cb.grid(row=row, column=col, sticky="w", padx=6, pady=4)
            col += 1
            if col >= 3:
                col = 0
                row += 1

        ttk.Label(elem_box, text="Custom sheets (comma-separated):").pack(anchor="w", padx=10, pady=(8,2))
        ttk.Entry(elem_box, textvariable=self.custom_sheets_var).pack(fill="x", padx=10, pady=(0,8))

        # Formatting
        fmt_box = ttk.LabelFrame(opt, text="Formatting")
        fmt_box.pack(side="left", padx=10, pady=8, fill="y")

        ttk.Label(fmt_box, text="Decimals:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Spinbox(fmt_box, from_=0, to=12, textvariable=self.decimals_var, width=5).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(fmt_box, text="Delimiter:").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        delim_menu = ttk.Combobox(fmt_box, width=10, textvariable=self.delim_var, state="readonly",
                                  values=["\\t", ",", " "])
        delim_menu.grid(row=1, column=1, padx=6, pady=6)

        ttk.Checkbutton(fmt_box, text='Append ".arx -xy" after .txt', variable=self.append_arx_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=6)
        ttk.Checkbutton(fmt_box, text="Zip results after export", variable=self.zip_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=6)

        # Output dir
        out_box = ttk.LabelFrame(opt, text="Output")
        out_box.pack(side="left", padx=10, pady=8, fill="y")

        ttk.Label(out_box, text="Output folder:").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Entry(out_box, textvariable=self.outdir_var, width=36).grid(row=0, column=1, padx=6, pady=6)
        ttk.Button(out_box, text="Browse...", command=self.browse_outdir).grid(row=0, column=2, padx=6, pady=6)

        # Bottom: run
        run_frame = ttk.Frame(self)
        run_frame.pack(fill="x", padx=10, pady=10)
        ttk.Button(run_frame, text="Export", command=self.export).pack(side="right")

        # Status
        self.status_var = tk.StringVar(value="Ready.")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.pack(fill="x", padx=10, pady=(0,10))

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Choose Excel files",
                                            filetypes=[("Excel files", "*.xlsx *.xls")])
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.file_list.insert("end", p)

    def remove_selected(self):
        sel = list(self.file_list.curselection())
        sel.reverse()
        for idx in sel:
            path = self.file_list.get(idx)
            self.files.remove(path)
            self.file_list.delete(idx)

    def clear_files(self):
        self.files.clear()
        self.file_list.delete(0, "end")

    def browse_outdir(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d:
            self.outdir_var.set(d)

    def _get_selected_sheets(self) -> List[str]:
        sheets = [sheet for key, sheet in DEFAULT_SHEETS.items() if self.element_vars[key].get()]
        custom = [s.strip() for s in self.custom_sheets_var.get().split(",") if s.strip()]
        return sheets + custom

    def export(self):
        try:
            if not self.files:
                messagebox.showwarning("No files", "Please add at least one Excel file.")
                return
            sheets = self._get_selected_sheets()
            if not sheets:
                messagebox.showwarning("No elements", "Please select at least one element or add a custom sheet name.")
                return

            outdir = self.outdir_var.get()
            os.makedirs(outdir, exist_ok=True)
            decimals = int(self.decimals_var.get())
            append_arx = self.append_arx_var.get()
            delim = {"\\t": "\t", ",": ",", " ": " "}[self.delim_var.get()]

            exported = []
            errors = []

            for fpath in self.files:
                fname = os.path.basename(fpath)
                base = os.path.splitext(fname)[0]
                try:
                    # For .xls, require xlrd
                    if fpath.lower().endswith(".xls"):
                        try:
                            xls = pd.ExcelFile(fpath, engine="xlrd")
                        except Exception as e:
                            raise RuntimeError("Reading .xls requires 'xlrd' (pip install xlrd).") from e
                    else:
                        xls = pd.ExcelFile(fpath)

                    for sheet in sheets:
                        if sheet not in xls.sheet_names:
                            continue
                        df = read_sheet_extract(fpath, sheet, decimals)
                        if df is None or df.empty:
                            continue
                        out_name = f"{base}_{sheet}.txt"
                        if append_arx:
                            out_name += ".arx -xy"
                        out_path = os.path.join(outdir, out_name)
                        export_txt(df, out_path, delimiter=delim)
                        exported.append(out_path)
                except Exception as e:
                    errors.append(f"{fname}: {e}")

            # Zip if requested
            zip_path = None
            if self.zip_var.get() and exported:
                import zipfile
                zip_name = "XPS_exports.zip"
                zip_path = os.path.join(outdir, zip_name)
                with zipfile.ZipFile(zip_path, "w") as zf:
                    for p in exported:
                        arcname = os.path.basename(p)
                        zf.write(p, arcname)

            msg = f"Exported {len(exported)} files."
            if zip_path:
                msg += f" Zipped at: {zip_path}"
            if errors:
                msg += f"\n\nSome files had issues:\n- " + "\n- ".join(errors)

            self.status_var.set("Done.")
            messagebox.showinfo("Complete", msg)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Unexpected error:\n{e}")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
