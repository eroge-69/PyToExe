#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import pandas as pd
from pandas.api.types import CategoricalDtype
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]
CAT = CategoricalDtype(categories=MONTHS, ordered=True)

def parse_date_safe(s):
    try:
        return pd.to_datetime(s, errors="coerce", dayfirst=True, infer_datetime_format=True)
    except Exception:
        return pd.to_datetime(s, errors="coerce")

class BirthdayManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Birthday Manager")
        self.geometry("880x540")
        self.filepath = None
        self.df = pd.DataFrame(columns=["Month","Gregorian Date","Name","Hijri Date"])

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)
        ttk.Button(top, text="Open Excel...", command=self.open_excel).pack(side="left")
        ttk.Button(top, text="Save As...", command=self.save_as).pack(side="left", padx=6)
        ttk.Button(top, text="Sort (Month order)", command=self.sort_df).pack(side="left", padx=6)
        ttk.Button(top, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=6)

        # Entry form
        form = ttk.LabelFrame(self, text="Add / Update Entry")
        form.pack(fill="x", padx=10, pady=8)

        self.name_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.hijri_var = tk.StringVar()

        ttk.Label(form, text="Name").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        ttk.Entry(form, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=6, pady=6)

        ttk.Label(form, text="Gregorian Date (e.g., 29 Oct 2024)").grid(row=0, column=2, padx=6, pady=6, sticky="e")
        ttk.Entry(form, textvariable=self.date_var, width=25).grid(row=0, column=3, padx=6, pady=6)

        ttk.Label(form, text="Hijri Date (optional, text)").grid(row=0, column=4, padx=6, pady=6, sticky="e")
        ttk.Entry(form, textvariable=self.hijri_var, width=25).grid(row=0, column=5, padx=6, pady=6)

        ttk.Button(form, text="Add / Update", command=self.add_update).grid(row=0, column=6, padx=6, pady=6)

        # Table
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=8)

        cols = ["Name","Gregorian Date","Month","Hijri Date"]
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=180 if c!="Hijri Date" else 220)
        self.tree.pack(fill="both", expand=True, side="left")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Status
        self.status = tk.StringVar(value="Open an Excel file to begin.")
        ttk.Label(self, textvariable=self.status).pack(fill="x", padx=10, pady=(0,10))

    def on_select(self, event):
        item = self.tree.selection()
        if not item:
            return
        idx = int(self.tree.item(item[0], "text"))
        row = self.df.iloc[idx]
        self.name_var.set(row.get("Name",""))
        self.date_var.set(row.get("Gregorian Date",""))
        self.hijri_var.set(row.get("Hijri Date",""))

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for i, row in self.df.iterrows():
            values = [row.get("Name",""), row.get("Gregorian Date",""), row.get("Month",""), row.get("Hijri Date","")]
            self.tree.insert("", "end", text=str(i), values=values)

        self.status.set(f"Loaded {len(self.df)} rows. {'Ready.' if self.filepath else ''}")

    def open_excel(self):
        p = filedialog.askopenfilename(
            title="Open Excel file",
            filetypes=[("Excel files","*.xlsx *.xlsm *.xls")]
        )
        if not p:
            return
        try:
            # Prefer a sheet named 'Data' or 'Birthday Calendar (Sorted)'; else first sheet
            xl = pd.ExcelFile(p)
            sheet_name = None
            for s in xl.sheet_names:
                sl = s.strip().lower()
                if sl in ["data", "birthday calendar (sorted)".lower(), "birthday calendar"]:
                    sheet_name = s
                    break
            if sheet_name is None:
                sheet_name = xl.sheet_names[0]

            df = pd.read_excel(p, sheet_name=sheet_name)

            # Normalize columns
            cols = {c.lower(): c for c in df.columns}
            month_col = cols.get("month")
            name_col = None
            greg_col = None
            hijri_col = None
            # try to detect logical names
            for k, v in cols.items():
                if k in ["name","names","full name"]:
                    name_col = v
                if "gregorian" in k and "date" in k:
                    greg_col = v
                if k in ["date","dob","birthdate","birthday"] and greg_col is None:
                    greg_col = v
                if "hijri" in k and "date" in k:
                    hijri_col = v
                if k == "hijri" and hijri_col is None:
                    hijri_col = v

            if month_col is None:
                # derive month from date
                if greg_col and greg_col in df.columns:
                    parsed = parse_date_safe(df[greg_col])
                    df["Month"] = parsed.dt.strftime("%B")
                else:
                    df["Month"] = ""
                month_col = "Month"

            # Build final frame
            keep_cols = {
                "Name": name_col if name_col in df.columns else "Name",
                "Gregorian Date": greg_col if greg_col in df.columns else "Gregorian Date",
                "Month": month_col,
                "Hijri Date": hijri_col if hijri_col in df.columns else "Hijri Date"
            }

            # Ensure columns exist
            for target, src in keep_cols.items():
                if src not in df.columns:
                    df[target] = ""
                elif target != src:
                    df[target] = df[src]

            self.df = df[["Name","Gregorian Date","Month","Hijri Date"]].copy()

            # Sort initially
            self.sort_df(update_table=False)
            self.filepath = p
            self.refresh_table()
            self.status.set(f"Opened: {os.path.basename(p)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file.\n{e}")

    def sort_df(self, update_table=True):
        if self.df.empty:
            return
        # month order
        self.df["Month"] = self.df["Month"].astype("string").str.strip().str.capitalize()
        self.df["_MonthOrder"] = self.df["Month"].astype(CAT)
        # day
        parsed = parse_date_safe(self.df["Gregorian Date"])
        if parsed.notna().any():
            self.df["_DayNum"] = parsed.dt.day.fillna(0).astype(int)
        else:
            # try to extract day from text like '10 Sep 2009'
            self.df["_DayNum"] = (
                self.df["Gregorian Date"].astype(str).str.extract(r"(^|\\s)(\\d{1,2})(st|nd|rd|th)?\\b", expand=False)[1]
                .astype(float)
                .fillna(0)
                .astype(int)
            )
        self.df["_idx"] = range(len(self.df))
        self.df = self.df.sort_values(by=["_MonthOrder","_DayNum","_idx"]).drop(columns=["_MonthOrder","_DayNum","_idx"]).reset_index(drop=True)
        if update_table:
            self.refresh_table()

    def add_update(self):
        name = self.name_var.get().strip()
        gdate = self.date_var.get().strip()
        hijri = self.hijri_var.get().strip()

        if not name or not gdate:
            messagebox.showwarning("Missing info", "Please provide at least Name and Gregorian Date.")
            return

        # Derive month
        parsed = parse_date_safe(gdate)
        if pd.isna(parsed):
            # try to keep month as-is if user gives a month string elsewhere
            month_name = ""
        else:
            month_name = parsed.strftime("%B")

        # If a row with same Name and Gregorian Date exists, update it; else append
        mask = (self.df["Name"].astype(str).str.lower()==name.lower()) & (self.df["Gregorian Date"].astype(str).str.lower()==gdate.lower())
        if mask.any():
            idx = mask.idxmax()
            self.df.loc[idx, ["Name","Gregorian Date","Month","Hijri Date"]] = [name, gdate, month_name, hijri]
        else:
            self.df.loc[len(self.df)] = [name, gdate, month_name, hijri]

        self.sort_df(update_table=True)
        self.name_var.set(""); self.date_var.set(""); self.hijri_var.set("")
        self.status.set("Entry added/updated.")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        idxs = sorted([int(self.tree.item(i, "text")) for i in sel], reverse=True)
        if messagebox.askyesno("Confirm", f"Delete {len(idxs)} selected row(s)?"):
            self.df.drop(index=idxs, inplace=True, errors="ignore")
            self.df.reset_index(drop=True, inplace=True)
            self.refresh_table()

    def save_as(self):
        if self.df.empty:
            messagebox.showwarning("Nothing to save", "No data to save yet.")
            return
        p = filedialog.asksaveasfilename(
            title="Save Excel As",
            defaultextension=".xlsx",
            filetypes=[("Excel Workbook","*.xlsx")]
        )
        if not p:
            return

        try:
            # If saving over an existing workbook, try to preserve other sheets by writing to a new file
            # We'll write a single sheet 'Data' to keep things clean.
            out_df = self.df.copy()
            # Month Number helper
            cat = CategoricalDtype(categories=MONTHS, ordered=True)
            out_df["Month Number"] = out_df["Month"].astype("string").astype(cat).cat.codes.replace({-1: None}) + 1
            with pd.ExcelWriter(p, engine="openpyxl") as writer:
                out_df.to_excel(writer, index=False, sheet_name="Data")
            self.status.set(f"Saved to {os.path.basename(p)}")
            messagebox.showinfo("Saved", f"Saved to:\n{p}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file.\n{e}")

if __name__ == "__main__":
    app = BirthdayManager()
    app.mainloop()
