#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HexConverterApp - Simple desktop app to convert Hex to Decimal.
Features:
- Convert entire hex or only the last 6 characters (e.g., a3af8e -> 10727310).
- Accepts optional "0x" prefix and ignores spaces/underscores.
- Copy result to clipboard.
- Conversion history with timestamps; export/import CSV.
- Small, clean Tkinter UI that runs on Windows/macOS/Linux.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime

APP_TITLE = "Hex Converter"
APP_VERSION = "1.0.0"

def normalize_hex(s: str) -> str:
    # strip whitespace and common separators
    s = s.strip().lower().replace(" ", "").replace("_", "")
    if s.startswith("0x"):
        s = s[2:]
    return s

def is_valid_hex(s: str) -> bool:
    if not s:
        return False
    for ch in s:
        if ch not in "0123456789abcdef":
            return False
    return True

def convert_hex(s: str, last6_only: bool = False) -> int:
    s = normalize_hex(s)
    if last6_only and len(s) > 6:
        s = s[-6:]
    if not is_valid_hex(s):
        raise ValueError("Invalid hex input.")
    return int(s, 16)

class HexConverterApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.master = master
        self.last6_var = tk.BooleanVar(value=False)
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        self.master.title(f"{APP_TITLE} v{APP_VERSION}")
        self.master.geometry("600x420")
        try:
            self.master.iconbitmap(default="")  # no icon bundled; placeholder
        except Exception:
            pass

        # Top: Input
        row = 0
        ttk.Label(self, text="Hex Input:").grid(row=row, column=0, sticky="w", padx=(0,8), pady=(0,6))
        entry = ttk.Entry(self, textvariable=self.input_var, width=50)
        entry.grid(row=row, column=1, columnspan=3, sticky="ew", pady=(0,6))
        entry.focus()

        # Options
        row += 1
        ttk.Checkbutton(self, text="Use last 6 digits only (…xxxxxx)", variable=self.last6_var).grid(
            row=row, column=1, sticky="w", pady=(0,6)
        )

        # Buttons
        row += 1
        btn_convert = ttk.Button(self, text="Convert", command=self.on_convert)
        btn_convert.grid(row=row, column=1, sticky="w")
        btn_clear = ttk.Button(self, text="Clear", command=self.on_clear)
        btn_clear.grid(row=row, column=2, sticky="w", padx=(8,0))
        btn_copy  = ttk.Button(self, text="Copy Result", command=self.on_copy)
        btn_copy.grid(row=row, column=3, sticky="e")

        # Output
        row += 1
        ttk.Label(self, text="Decimal Output:").grid(row=row, column=0, sticky="w", pady=(10,4))
        out = ttk.Entry(self, textvariable=self.output_var, state="readonly")
        out.grid(row=row, column=1, columnspan=3, sticky="ew", pady=(10,4))

        # History
        row += 1
        ttk.Label(self, text="History:").grid(row=row, column=0, sticky="w", pady=(10,4))
        self.hist = tk.Listbox(self, height=10)
        self.hist.grid(row=row, column=1, columnspan=3, sticky="nsew", pady=(10,4))

        # Status bar
        row += 1
        sep = ttk.Separator(self, orient="horizontal")
        sep.grid(row=row, column=0, columnspan=4, sticky="ew", pady=(8,4))
        row += 1
        status = ttk.Label(self, textvariable=self.status_var, anchor="w")
        status.grid(row=row, column=0, columnspan=4, sticky="ew")

        # History buttons
        row += 1
        btn_export = ttk.Button(self, text="Export CSV", command=self.on_export)
        btn_export.grid(row=row, column=1, sticky="w", pady=(8,0))
        btn_import = ttk.Button(self, text="Import CSV", command=self.on_import)
        btn_import.grid(row=row, column=2, sticky="w", padx=(8,0), pady=(8,0))

        # Configure weights
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.rowconfigure(5, weight=1)  # history grows

        # Menu
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Export CSV…", command=self.on_export)
        filemenu.add_command(label="Import CSV…", command=self.on_import)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.destroy)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.on_about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.master.config(menu=menubar)

        self.pack(fill="both", expand=True)

        # Apply ttk theme tweaks
        style = ttk.Style()
        try:
            if self.master.tk.call("ttk::style", "theme", "use") in ("vista", "xpnative", "winnative"):
                pass
            else:
                style.theme_use("clam")
        except Exception:
            pass

    def _bind_events(self):
        self.master.bind("<Return>", lambda e: self.on_convert())
        self.hist.bind("<Double-1>", self.on_hist_double_click)

    def on_convert(self):
        text = self.input_var.get()
        try:
            result = convert_hex(text, self.last6_var.get())
            self.output_var.set(str(result))
            when = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mode = "last6" if self.last6_var.get() else "full"
            self.hist.insert(0, f"[{when}] {text} ({mode}) -> {result}")
            self.status_var.set("Converted successfully.")
        except Exception as ex:
            from tkinter import messagebox
            messagebox.showerror("Conversion Error", f"{ex}")
            self.status_var.set("Error: invalid input.")

    def on_clear(self):
        self.input_var.set("")
        self.output_var.set("")
        self.status_var.set("Cleared.")

    def on_copy(self):
        val = self.output_var.get()
        if not val:
            self.status_var.set("Nothing to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(val)
        self.status_var.set("Result copied to clipboard.")

    def on_export(self):
        if self.hist.size() == 0:
            from tkinter import messagebox
            messagebox.showinfo("Export CSV", "No history to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files","*.csv"), ("All files","*.*")],
            title="Export history to CSV"
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["timestamp","input","mode","decimal"])
                for i in range(self.hist.size()-1, -1, -1):  # oldest to newest
                    row = self.hist.get(i)
                    # row format: [YYYY-mm-dd HH:MM:SS] input (mode) -> result
                    try:
                        ts = row.split("]")[0][1:]
                        rest = row.split("] ")[1]
                        inp = rest.split(" (")[0]
                        mode = rest.split(" (")[1].split(")")[0]
                        dec = rest.split("->")[1].strip()
                        writer.writerow([ts, inp, mode, dec])
                    except Exception:
                        # if parsing fails, write entire line in first column
                        writer.writerow([row])
            self.status_var.set(f"Exported to {path}")
        except Exception as ex:
            from tkinter import messagebox
            messagebox.showerror("Export Error", f"{ex}")

    def on_import(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV files","*.csv"), ("All files","*.*")],
            title="Import history from CSV"
        )
        if not path:
            return
        try:
            with open(path, "r", newline="", encoding="utf-8") as f:
                import csv
                reader = csv.reader(f)
                header_skipped = False
                count = 0
                for row in reader:
                    if not header_skipped:
                        header_skipped = True
                        # detect if header
                        if row and row[0].lower().startswith("timestamp"):
                            continue
                    if len(row) >= 4:
                        ts, inp, mode, dec = row[:4]
                        self.hist.insert(0, f"[{ts}] {inp} ({mode}) -> {dec}")
                        count += 1
                    else:
                        # single-column fallback
                        self.hist.insert(0, row[0])
                        count += 1
            self.status_var.set(f"Imported {count} rows.")
        except Exception as ex:
            from tkinter import messagebox
            messagebox.showerror("Import Error", f"{ex}")

    def on_hist_double_click(self, event):
        sel = self.hist.curselection()
        if not sel:
            return
        line = self.hist.get(sel[0])
        try:
            # reuse input for quick reconvert
            inp = line.split("] ")[1].split(" (")[0]
            mode = line.split(" (")[1].split(")")[0]
            self.input_var.set(inp)
            self.last6_var.set(mode == "last6")
            self.status_var.set("Loaded to input from history.")
        except Exception:
            pass

    def on_about(self):
        from tkinter import messagebox
        messagebox.showinfo(
            "About",
            f"{APP_TITLE} v{APP_VERSION}\n\nA tiny GUI to convert hex to decimal.\n"
            "• Full hex or last 6 digits mode\n"
            "• Copy result, history, CSV export/import\n\n"
            "Built with Tkinter (Python)."
        )

def main():
    root = tk.Tk()
    app = HexConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
