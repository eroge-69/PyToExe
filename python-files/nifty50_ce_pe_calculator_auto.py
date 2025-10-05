# nifty50_ce_pe_calculator_auto.py
# Nifty 50 CE & PE Calculator with Auto Refresh + CSV Export
# Build exe: pyinstaller --onefile --windowed nifty50_ce_pe_calculator_auto.py

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import csv
import os

def safe_float(v):
    try:
        return float(v)
    except:
        return None

class NiftyAutoCalc(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nifty 50 CE & PE Auto Calculator")
        self.geometry("580x460")
        self.resizable(False, False)
        self.create_widgets()
        self.bind_events()

    def create_widgets(self):
        ttk.Label(self, text="📈 Nifty 50 Calculator for CE & PE", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # --- Nifty Inputs ---
        frm_nifty = ttk.LabelFrame(self, text="Nifty Inputs")
        frm_nifty.pack(pady=8, padx=10, fill="x")

        ttk.Label(frm_nifty, text="Nifty50 Value ①:").grid(row=0, column=0, padx=5, pady=5)
        self.nifty1_var = tk.StringVar()
        ttk.Entry(frm_nifty, textvariable=self.nifty1_var, width=14).grid(row=0, column=1)

        ttk.Label(frm_nifty, text="Nifty50 Value ②:").grid(row=0, column=2, padx=5)
        self.nifty2_var = tk.StringVar()
        ttk.Entry(frm_nifty, textvariable=self.nifty2_var, width=14).grid(row=0, column=3)

        ttk.Label(frm_nifty, text="Ans① (ΔNifty):").grid(row=1, column=0, padx=5)
        self.ans1_var = tk.StringVar(value="0.00")
        ttk.Entry(frm_nifty, textvariable=self.ans1_var, width=14, state="readonly").grid(row=1, column=1)

        ttk.Label(frm_nifty, text="Ans② (Δ×0.4):").grid(row=1, column=2, padx=5)
        self.ans2_var = tk.StringVar(value="0.00")
        ttk.Entry(frm_nifty, textvariable=self.ans2_var, width=14, state="readonly").grid(row=1, column=3)

        # --- CE Section ---
        frm_ce = ttk.LabelFrame(self, text="CE Calculation")
        frm_ce.pack(pady=8, padx=10, fill="x")

        ttk.Label(frm_ce, text="CE Value:").grid(row=0, column=0, padx=5, pady=5)
        self.ce_var = tk.StringVar()
        ttk.Entry(frm_ce, textvariable=self.ce_var, width=14).grid(row=0, column=1)

        ttk.Label(frm_ce, text="+ Ans② =").grid(row=0, column=2)
        self.ce_plus_var = tk.StringVar(value="0.00")
        ttk.Entry(frm_ce, textvariable=self.ce_plus_var, state="readonly", width=14).grid(row=0, column=3)

        ttk.Label(frm_ce, text="− Ans② =").grid(row=0, column=4)
        self.ce_minus_var = tk.StringVar(value="0.00")
        ttk.Entry(frm_ce, textvariable=self.ce_minus_var, state="readonly", width=14).grid(row=0, column=5)

        # --- PE Section ---
        frm_pe = ttk.LabelFrame(self, text="PE Calculation")
        frm_pe.pack(pady=8, padx=10, fill="x")

        ttk.Label(frm_pe, text="PE Value:").grid(row=0, column=0, padx=5, pady=5)
        self.pe_var = tk.StringVar()
        ttk.Entry(frm_pe, textvariable=self.pe_var, width=14).grid(row=0, column=1)

        ttk.Label(frm_pe, text="+ Ans② =").grid(row=0, column=2)
        self.pe_plus_var = tk.StringVar(value="0.00")
        ttk.Entry(frm_pe, textvariable=self.pe_plus_var, state="readonly", width=14).grid(row=0, column=3)

        ttk.Label(frm_pe, text="− Ans② =").grid(row=0, column=4)
        self.pe_minus_var = tk.StringVar(value="0.00")
        ttk.Entry(frm_pe, textvariable=self.pe_minus_var, state="readonly", width=14).grid(row=0, column=5)

        # --- Buttons ---
        frm_btn = ttk.Frame(self)
        frm_btn.pack(pady=10)
        ttk.Button(frm_btn, text="💾 Export to CSV", command=self.export_csv).grid(row=0, column=0, padx=8)
        ttk.Button(frm_btn, text="🧹 Clear All", command=self.clear_all).grid(row=0, column=1, padx=8)
        ttk.Button(frm_btn, text="❌ Exit", command=self.quit).grid(row=0, column=2, padx=8)

        # --- Display All Answers ---
        self.summary_lbl = ttk.Label(self, text="", font=("Segoe UI", 10, "bold"), foreground="blue")
        self.summary_lbl.pack(pady=10)

    def bind_events(self):
        # Auto refresh on typing
        for var in [self.nifty1_var, self.nifty2_var, self.ce_var, self.pe_var]:
            var.trace_add("write", lambda *args: self.update_all())

    def update_all(self):
        n1 = safe_float(self.nifty1_var.get())
        n2 = safe_float(self.nifty2_var.get())
        ce = safe_float(self.ce_var.get())
        pe = safe_float(self.pe_var.get())

        ans1 = ans2 = 0.0
        if n1 is not None and n2 is not None:
            ans1 = n1 - n2
            ans2 = ans1 * 0.4
            self.ans1_var.set(f"{ans1:.2f}")
            self.ans2_var.set(f"{ans2:.2f}")
        else:
            self.ans1_var.set("0.00")
            self.ans2_var.set("0.00")

        if ce is not None:
            self.ce_plus_var.set(f"{ce + ans2:.2f}")
            self.ce_minus_var.set(f"{ce - ans2:.2f}")
        else:
            self.ce_plus_var.set("0.00")
            self.ce_minus_var.set("0.00")

        if pe is not None:
            self.pe_plus_var.set(f"{pe + ans2:.2f}")
            self.pe_minus_var.set(f"{pe - ans2:.2f}")
        else:
            self.pe_plus_var.set("0.00")
            self.pe_minus_var.set("0.00")

        self.summary_lbl.config(
            text=f"Ans①={ans1:.2f}, Ans②={ans2:.2f}, CE(+)= {self.ce_plus_var.get()}, CE(-)= {self.ce_minus_var.get()}, "
                f"PE(+)= {self.pe_plus_var.get()}, PE(-)= {self.pe_minus_var.get()}"
        )

    def clear_all(self):
        for var in [
            self.nifty1_var, self.nifty2_var, self.ce_var, self.pe_var,
            self.ans1_var, self.ans2_var, self.ce_plus_var, self.ce_minus_var,
            self.pe_plus_var, self.pe_minus_var
        ]:
            var.set("")
        self.summary_lbl.config(text="")

    def export_csv(self):
        # Ensure Ans2 calculated
        ans2 = safe_float(self.ans2_var.get())
        if ans2 is None or ans2 == 0:
            messagebox.showwarning("Warning", "Please enter valid Nifty values before exporting.")
            return

        data = {
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Nifty1": self.nifty1_var.get(),
            "Nifty2": self.nifty2_var.get(),
            "Ans1": self.ans1_var.get(),
            "Ans2": self.ans2_var.get(),
            "CE": self.ce_var.get(),
            "CE+": self.ce_plus_var.get(),
            "CE-": self.ce_minus_var.get(),
            "PE": self.pe_var.get(),
            "PE+": self.pe_plus_var.get(),
            "PE-": self.pe_minus_var.get(),
        }

        file = "nifty_calculations.csv"
        file_exists = os.path.isfile(file)

        with open(file, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

        messagebox.showinfo("Exported ✅", f"Data saved to {file}")

if __name__ == "__main__":
    app = NiftyAutoCalc()
    app.mainloop()
